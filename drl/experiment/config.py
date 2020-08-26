import os
from typing import List

from drl.experiment.configuration.experiment_config import ExperimentConfig
from drl.experiment.configuration.master_config import MasterConfig


class Config:
    def __init__(self, current_exp='lunarlander', test_flag=False, exp_cfg=None):
        self.__app = self.__set_app_config()
        self.__exp_cfg = self.__set_exp_config(exp_cfg)

        self.__exp_cfg.set_current(current_exp)

        self.__test = test_flag

    def get_app_config(self):
        return self.__app

    def get_exp_ids(self) -> List[str]:
        return self.__exp_cfg.get_ids()

    def set_current_exp_cfg(self, exp_id):
        self.__exp_cfg.set_current(exp_id)

    def get_current_exp_cfg(self) -> ExperimentConfig:
        return self.__exp_cfg.get_current()

    # app
    def get_app_analysis_path(self, train_mode=True):

        if self.__test:
            if train_mode:
                return os.path.join(self.__app['path_tests'], self.__app['path_experiments'], 'analysis')
            else:
                return os.path.join(self.__app['path_tests'], self.__app['path_experiments'], 'analysis')
        else:
            if train_mode:
                return os.path.join(self.__app['path_experiments'], 'analysis')
            else:
                return os.path.join(self.__app['path_experiments'], 'analysis')

    def get_app_experiments_path(self, train_mode=True):

        if self.__test:
            if train_mode:
                return os.path.join(self.__app['path_tests'], self.__app['path_experiments'], self.__app['path_train'])
            else:
                return os.path.join(self.__app['path_tests'], self.__app['path_experiments'], self.__app['path_play'])
        else:
            if train_mode:
                return os.path.join(self.__app['path_experiments'], self.__app['path_train'])
            else:
                return os.path.join(self.__app['path_experiments'], self.__app['path_play'])

    def __set_app_config(self):
        return {
            'path_experiments': '_experiments',
            'path_tests': '_tests',
            'path_play': 'play',
            'path_train': 'train',
        }

    def __set_exp_config(self, cfg) -> MasterConfig:

        if cfg is not None:
            return MasterConfig.from_json(cfg)

        cfg = {
            "experiment_cfgs": [
                 {
                    "id": "lunarlander",
                    "gym_id": "LunarLander-v2",
                    "agent_cfg": {
                        "action_size": 4,
                        "discrete": True,
                        "num_frames": 1,
                        "state_rgb": False,
                        "state_size": 8
                    },
                    "environment_cfg": {
                        "env_type": "gym"
                    },
                    "neural_network_cfg": {
                        "hidden_layers": [
                            64,
                            64
                        ]
                    },
                    "reinforcement_learning_cfg": {
                        "algorithm_type": "dqn"
                    },
                    "replay_memory_cfg": {
                        "buffer_size": 100000,
                        "prioritized_replay": True,
                        "prioritized_replay_alpha": 0.6,
                        "prioritized_replay_beta0": 0.4,
                        "prioritized_replay_eps": 1e-06
                    },
                    "trainer_cfg": {
                        "batch_size": 64,
                        "epsilon_decay": 0.995,
                        "epsilon_max": 1,
                        "epsilon_min": 0.01,
                        "eval_frequency": 20000,
                        "eval_steps": 3000,
                        "gamma": 0.99,
                        "human_flag": False,
                        "learning_rate": 0.0001,
                        "max_episode_steps": 1000,
                        "max_steps": 1000000,
                        "tau": 0.001,
                        "update_every": 4
                    }
                },
                {
                    "id": "breakout",
                    "gym_id": "Breakout-ram-v4",
                    "agent_cfg": {
                        "action_size": 3,
                        "discrete": True,
                        "num_frames": 1,
                        "state_rgb": False,
                        "state_size": 128
                    },
                    "environment_cfg": {
                        "env_type": "spaceinvaders_atari_gym"
                    },
                    "neural_network_cfg": {
                        "hidden_layers": [
                            64,
                            64
                        ]
                    },
                    "reinforcement_learning_cfg": {
                        "algorithm_type": "dqn"
                    },
                    "replay_memory_cfg": {
                        "buffer_size": 100000,
                        "prioritized_replay": True,
                        "prioritized_replay_alpha": 0.6,
                        "prioritized_replay_beta0": 0.4,
                        "prioritized_replay_eps": 1e-06
                    },
                    "trainer_cfg": {
                        "batch_size": 64,
                        "epsilon_decay": 0.995,
                        "epsilon_max": 1,
                        "epsilon_min": 0.01,
                        "eval_frequency": 20000,
                        "eval_steps": 3000,
                        "gamma": 0.99,
                        "human_flag": True,
                        "learning_rate": 0.0001,
                        "max_episode_steps": 1000,
                        "max_steps": 1000000,
                        "tau": 0.001,
                        "update_every": 4
                    }
                },
                {
                    "id": "breakout-rgb",
                    "gym_id": "Breakout-v4",
                    "agent_cfg": {
                        "action_size": 3,
                        "discrete": True,
                        "num_frames": 1,
                        "state_rgb": True,
                        "state_size": [80, 80]
                    },
                    "environment_cfg": {
                        "env_type": "spaceinvaders_atari_gym"
                    },
                    "neural_network_cfg": {
                        "hidden_layers": [
                            64,
                            64
                        ]
                    },
                    "reinforcement_learning_cfg": {
                        "algorithm_type": "dqn"
                    },
                    "replay_memory_cfg": {
                        "buffer_size": 100000,
                        "prioritized_replay": True,
                        "prioritized_replay_alpha": 0.6,
                        "prioritized_replay_beta0": 0.4,
                        "prioritized_replay_eps": 1e-06
                    },
                    "trainer_cfg": {
                        "batch_size": 64,
                        "epsilon_decay": 0.995,
                        "epsilon_max": 1,
                        "epsilon_min": 0.01,
                        "eval_frequency": 20000,
                        "eval_steps": 3000,
                        "gamma": 0.99,
                        "human_flag": False,
                        "learning_rate": 0.0001,
                        "max_episode_steps": 1000,
                        "max_steps": 1000000,
                        "tau": 0.001,
                        "update_every": 4
                    }
                },
                {
                    'id': 'banana',
                    'gym_id': 'env/unity/mac/banana',
                    "agent_cfg": {
                        "action_size": 4,
                        "discrete": True,
                        "num_frames": 1,
                        "state_rgb": False,
                        "state_size": 8
                    },
                    "environment_cfg": {
                        "env_type": "gym"
                    },
                    "neural_network_cfg": {
                        "hidden_layers": [
                            64,
                            64
                        ]
                    },
                    "reinforcement_learning_cfg": {
                        "algorithm_type": "dqn_double"
                    },
                    "replay_memory_cfg": {
                        "buffer_size": 100000,
                        "prioritized_replay": True,
                        "prioritized_replay_alpha": 0.6,
                        "prioritized_replay_beta0": 0.4,
                        "prioritized_replay_eps": 1e-06
                    },
                    "trainer_cfg": {
                        "batch_size": 64,
                        "epsilon_decay": 0.995,
                        "epsilon_max": 1,
                        "epsilon_min": 0.01,
                        "eval_frequency": 10200,
                        "eval_steps": 2100,
                        "gamma": 0.99,
                        "human_flag": False,
                        "learning_rate": 0.0001,
                        "max_episode_steps": 1000,
                        "max_steps": 600000,
                        "tau": 0.001,
                        "update_every": 4
                    }
                }
            ]
        }

        return MasterConfig.from_json(cfg)