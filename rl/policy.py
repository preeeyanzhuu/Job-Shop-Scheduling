import torch as th
import torch.nn as nn
from gymnasium import spaces
from sb3_contrib.common.maskable.policies import MaskableMultiInputActorCriticPolicy
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor


class JobScoringExtractor(BaseFeaturesExtractor):

    def __init__(self, observation_space: spaces.Dict, hidden: int = 64):
        n_slots = observation_space["mask"].shape[0]
        n_feat = observation_space["jobs"].shape[1]
        super().__init__(observation_space, features_dim=n_slots + hidden)
        self.n_slots, self.hidden = n_slots, hidden
        self.row_net = nn.Sequential(nn.Linear(n_feat, hidden), nn.ReLU(),
                                     nn.Linear(hidden, hidden), nn.ReLU())
        self.score_net = nn.Sequential(nn.Linear(2 * hidden, hidden), nn.ReLU(),
                                       nn.Linear(hidden, 1))

    def forward(self, obs):
        jobs, mask = obs["jobs"], obs["mask"]              
        h = self.row_net(jobs)                                
        m = (mask > 0.5).float().unsqueeze(-1)         
        ctx = (h * m).sum(1) / m.sum(1).clamp(min=1.0)      
        scores = self.score_net(th.cat([h, ctx.unsqueeze(1).expand_as(h)], dim=-1)).squeeze(-1)
        return th.cat([scores, ctx], dim=1)              


class _Heads(nn.Module):

    def __init__(self, n_slots: int, hidden: int):
        super().__init__()
        self.n_slots = n_slots
        self.latent_dim_pi = n_slots
        self.latent_dim_vf = hidden
        self.critic = nn.Sequential(nn.Linear(hidden, hidden), nn.ReLU(),
                                    nn.Linear(hidden, hidden), nn.ReLU())

    def forward(self, features):
        return self.forward_actor(features), self.forward_critic(features)

    def forward_actor(self, features):
        return features[:, :self.n_slots]

    def forward_critic(self, features):
        return self.critic(features[:, self.n_slots:])


class JobScorerPolicy(MaskableMultiInputActorCriticPolicy):

    def _build_mlp_extractor(self) -> None:
        fe = self.features_extractor
        self.mlp_extractor = _Heads(fe.n_slots, fe.hidden)

    def _build(self, lr_schedule) -> None:
        super()._build(lr_schedule)
        self.action_net = nn.Identity()            
        last = self.features_extractor.score_net[-1]  
        nn.init.orthogonal_(last.weight, gain=0.01)
        nn.init.zeros_(last.bias)
        self.optimizer = self.optimizer_class(self.parameters(), lr=lr_schedule(1), **self.optimizer_kwargs)