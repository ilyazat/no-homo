from pathlib import Path
from typing import Union
from fabric import Connection

from deeppavlov_dreamtools import DreamDist

DREAM_ROOT = Path(__file__).parents[3] / "dream"


class Deployer:
    async def deploy(self, dist: DreamDist, dream_root_remote):
        raise NotImplementedError


class SwarmDeployer(Deployer):
    def __init__(self, host: str, password: str, user: str, port: int = 22):
        """
        ...
        """
        self.user = user
        self.connection = Connection(host=host, port=port, user=user, connect_kwargs={"password": password})

    def init(self):
        self.connection.run("docker swarm init")

    def deploy(self, dist: DreamDist, dream_root_remote: Union[Path, str]):
        # command = self._get_dockercompose_up_command_from_dist(dist)
        # raise Exception(command)
        self.connection.run("docker stack deploy -c /home/doc/docker-compose.yml test")

    def service_list(self):
        self.connection.run("docker service list")

    def leave(self):
        self.connection.run("docker swarm leave --force")

    @staticmethod
    def _get_dockercompose_up_command_from_dist(dist: DreamDist) -> str:
        """
        Creates docker-compose up command depending on the loaded configs in the DreamDistribution

        Args:
             dist: DreamDistribution instance
        Returns:
            command in format of 'docker-compose [-f loaded configs pathfile] up'
        """
        config_command_list = []
        dist_path_str = str(dist.resolve_dist_path(dist.name, dist.dream_root)) + "/"
        dist_path_str = "/home/doc/dream/assistant_dists/dream/"

        compose_override_command = (
            f"-c {dist_path_str + dist.compose_override.DEFAULT_FILE_NAME}" if dist.compose_override else None
        )

        proxy_command = f"-c {dist_path_str + dist.compose_proxy.DEFAULT_FILE_NAME}" if dist.compose_proxy else None

        dev_command = f"-c {dist_path_str + dist.compose_dev.DEFAULT_FILE_NAME}" if dist.compose_dev else None

        config_commands_list = [compose_override_command, proxy_command, dev_command]
        for command in config_commands_list:
            if command:
                config_command_list.append(command)

        command = " ".join(config_commands_list)

        return f"docker stack deploy {command} up"


if __name__ == "__main__":
    dist = DreamDist.from_name(name="dream", dream_root=DREAM_ROOT)
    deployer = SwarmDeployer(host="127.0.0.1", user="doc", password="ghbdtnghbdtn", port=2222)
    deployer.deploy(dist, DREAM_ROOT)
    deployer.service_list()


