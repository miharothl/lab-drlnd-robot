import numpy as np
import random
import copy
from collections import namedtuple, deque


import torch
import torch.nn.functional as F
import torch.optim as optim

from drl.experiment.configuration import Configuration
from drl.model.ddpg_model import Actor, Critic, ActorPendulum, CriticPendulum

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


class DdpgAgent():
    """Interacts with and learns from the environment."""

    def __init__(self, seed, cfg: Configuration):
        """Initialize an Agent object.
        
        Params
        ======
            state_size (int): dimension of each state
            action_size (int): dimension of each action
            random_seed (int): random seed
        """

        rl_cfg = cfg.get_current_exp_cfg().reinforcement_learning_cfg
        trainer_cfg = cfg.get_current_exp_cfg().trainer_cfg
        replay_memory_cfg = cfg.get_current_exp_cfg().replay_memory_cfg

        self.BUFFER_SIZE = int(1e6)  # replay buffer size
        self.BATCH_SIZE = 128        # minibatch size
        self.GAMMA = 0.99            # discount factor
        self.TAU = 1e-3              # for soft update of target parameters
        self.LR_ACTOR = 1e-4         # learning rate of the actor
        self.LR_CRITIC = 3e-4        # learning rate of the critic
        self.WEIGHT_DECAY = 0.0001   # L2 weight decay

        self.BUFFER_SIZE = replay_memory_cfg.buffer_size
        self.BATCH_SIZE = trainer_cfg.batch_size
        self.GAMMA = trainer_cfg.gamma
        self.TAU = trainer_cfg.tau
        self.LR_ACTOR = rl_cfg.ddpg_cfg.lr_actor
        self.LR_CRITIC = rl_cfg.ddpg_cfg.lr_critic
        self.WEIGHT_DECAY = rl_cfg.ddpg_cfg.weight_decay

        self.state_size = cfg.get_current_exp_cfg().agent_cfg.state_size
        self.action_size = cfg.get_current_exp_cfg().agent_cfg.action_size
        self.seed = random.seed(seed)

        # Actor Network (w/ Target Network)
        self.actor_local = ActorPendulum(self.state_size, self.action_size, seed).to(device)
        self.actor_target = ActorPendulum(self.state_size, self.action_size, seed).to(device)
        self.actor_optimizer = optim.Adam(self.actor_local.parameters(), lr=self.LR_ACTOR)

        # Critic Network (w/ Target Network)
        self.critic_local = CriticPendulum(self.state_size, self.action_size, seed).to(device)
        self.critic_target = CriticPendulum(self.state_size, self.action_size, seed).to(device)
        self.critic_optimizer = optim.Adam(self.critic_local.parameters(), lr=self.LR_CRITIC, weight_decay=self.WEIGHT_DECAY)

        # Noise process
        self.noise = OUNoise(self.action_size, seed)

        # Replay memory
        self.memory = ReplayBuffer(self.action_size, self.BUFFER_SIZE, self.BATCH_SIZE, seed)
    
    def step(self, state, action, reward, next_state, done):
        """Save experience in replay memory, and use random sample from buffer to learn."""
        # Save experience / reward
        self.memory.add(state, action, reward, next_state, done)

        # Learn, if enough samples are available in memory
        if len(self.memory) > self.BATCH_SIZE:
            experiences = self.memory.sample()
            self.learn(experiences, self.GAMMA)

        return 0, 0, 0, 0

    def act(self, state, add_noise=True):
        """Returns actions for given state as per current policy."""
        state = torch.from_numpy(state).float().to(device)
        self.actor_local.eval()
        with torch.no_grad():
            action = self.actor_local(state).cpu().data.numpy()
        self.actor_local.train()
        if add_noise:
            action += self.noise.sample()
        return np.clip(action, -1, 1)

    def reset(self):
        self.noise.reset()

    def learn(self, experiences, gamma):
        """Update policy and value parameters using given batch of experience tuples.
        Q_targets = r + γ * critic_target(next_state, actor_target(next_state))
        where:
            actor_target(state) -> action
            critic_target(state, action) -> Q-value

        Params
        ======
            experiences (Tuple[torch.Tensor]): tuple of (s, a, r, s', done) tuples 
            gamma (float): discount factor
        """
        states, actions, rewards, next_states, dones = experiences

        # ---------------------------- update critic ---------------------------- #
        # Get predicted next-state actions and Q values from target models
        actions_next = self.actor_target(next_states)
        Q_targets_next = self.critic_target(next_states, actions_next)
        # Compute Q targets for current states (y_i)
        Q_targets = rewards + (gamma * Q_targets_next * (1 - dones))
        # Compute critic loss
        Q_expected = self.critic_local(states, actions)
        critic_loss = F.mse_loss(Q_expected, Q_targets)
        # Minimize the loss
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()

        # ---------------------------- update actor ---------------------------- #
        # Compute actor loss
        actions_pred = self.actor_local(states)
        actor_loss = -self.critic_local(states, actions_pred).mean()
        # Minimize the loss
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()

        # ----------------------- update target networks ----------------------- #
        self.soft_update(self.critic_local, self.critic_target, self.TAU)
        self.soft_update(self.actor_local, self.actor_target, self.TAU)

    def soft_update(self, local_model, target_model, tau):
        """Soft update model parameters.
        θ_target = τ*θ_local + (1 - τ)*θ_target

        Params
        ======
            local_model: PyTorch model (weights will be copied from)
            target_model: PyTorch model (weights will be copied to)
            tau (float): interpolation parameter 
        """
        for target_param, local_param in zip(target_model.parameters(), local_model.parameters()):
            target_param.data.copy_(tau*local_param.data + (1.0-tau)*target_param.data)

    def pre_process(self, state):
        return state

    def get_models(self):

        model_actor = namedtuple('name', 'weights')
        model_actor.name = 'current_actor'
        model_actor.weights = self.actor_local

        model_critic = namedtuple('name', 'weights')
        model_critic.name = 'current_critic'
        model_critic.weights = self.critic_local

        return [model_actor, model_critic]

class OUNoise:
    """Ornstein-Uhlenbeck process."""

    def __init__(self, size, seed, mu=0., theta=0.15, sigma=0.2):
        """Initialize parameters and noise process."""
        self.mu = mu * np.ones(size)
        self.theta = theta
        self.sigma = sigma
        self.seed = random.seed(seed)
        self.reset()

    def reset(self):
        """Reset the internal state (= noise) to mean (mu)."""
        self.state = copy.copy(self.mu)

    def sample(self):
        """Update internal state and return it as a noise sample."""
        x = self.state
        dx = self.theta * (self.mu - x) + self.sigma * np.array([random.random() for i in range(len(x))])
        self.state = x + dx
        return self.state



class ReplayBuffer:
    """Fixed-size buffer to store experience tuples."""

    def __init__(self, action_size, buffer_size, batch_size, seed):
        """Initialize a ReplayBuffer object.
        Params
        ======
            buffer_size (int): maximum size of buffer
            batch_size (int): size of each training batch
        """
        self.action_size = action_size
        self.memory = deque(maxlen=int(buffer_size))  # internal memory (deque)
        self.batch_size = batch_size
        self.experience = namedtuple("Experience", field_names=["state", "action", "reward", "next_state", "done"])
        self.seed = random.seed(seed)

    def add(self, state, action, reward, next_state, done):
        """Add a new experience to memory."""
        e = self.experience(state, action, reward, next_state, done)
        self.memory.append(e)



    def sample(self):
        """Randomly sample a batch of experiences from memory."""
        experiences = random.sample(self.memory, k=self.batch_size)

        states = torch.from_numpy(np.vstack([e.state for e in experiences if e is not None])).float().to(device)
        actions = torch.from_numpy(np.vstack([e.action for e in experiences if e is not None])).float().to(device)
        rewards = torch.from_numpy(np.vstack([e.reward for e in experiences if e is not None])).float().to(device)
        next_states = torch.from_numpy(np.vstack([e.next_state for e in experiences if e is not None])).float().to(device)
        dones = torch.from_numpy(np.vstack([e.done for e in experiences if e is not None]).astype(np.uint8)).float().to(device)

        return (states, actions, rewards, next_states, dones)

    def __len__(self):
        """Return the current size of internal memory."""
        return len(self.memory)