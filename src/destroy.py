import ast
import os
import subprocess
import uuid
from digitalai.release.integration import BaseTask


class Destroy(BaseTask):

    def execute(self) -> None:
        current_directory = os.getcwd()
        try:
            required_fields = ['gitUrl']
            for field in required_fields:
                if not self.input_properties.get(field):
                    raise ValueError(f"{field} field cannot be empty")

            git_url = self.input_properties['gitUrl']
            git_dir_path = self.input_properties['gitDirPath']
            git_token = self.input_properties['gitToken']
            branch = self.input_properties['branch']
            environment_variables = self.input_properties['environmentVariables']

            random_name = uuid.uuid4().hex[:6]
            clone_dir = f"{random_name}-clone"
            clone_command = ["git", "clone"]
            if git_token:
                clone_command.append(f"{git_url.replace('https://', f'https://{git_token}@')}")
            else:
                clone_command.append(git_url)
            clone_command.append(clone_dir)
            if branch:
                clone_command.extend(["--branch", branch])
            clone_process = subprocess.run(clone_command, text=True)
            if clone_process.returncode != 0:
                raise Exception("Git clone command failed: For more information, please check the 'View logs' section")

            if git_dir_path:
                clone_dir = clone_dir + "/" + git_dir_path

            os.chdir(clone_dir)
            try:
                if environment_variables:
                    environment_variables = ast.literal_eval(environment_variables)
                else:
                    environment_variables = {}
            except Exception as e:
                raise Exception(f"Error parsing environment variables: {e}")
            env_vars = os.environ.copy()
            env_vars.update(environment_variables)

            init_process = subprocess.run(["terraform", "init"], env=env_vars, text=True)
            if init_process.returncode != 0:
                raise Exception("Init command failed: For more information, please check the 'View logs' section")

            destroy_process = subprocess.run(["terraform", "destroy", "-auto-approve"], env=env_vars, text=True)
            if destroy_process.returncode != 0:
                raise Exception("Destroy command failed: For more information, please check the 'View logs' section")
            else:
                self.add_comment("Destroy command successfully executed: For more information, please check the 'View logs' section")

            # Remove environment variables from os.environ
            for key in environment_variables:
                os.environ.pop(key, None)

        except Exception as e:
            self.set_exit_code(1)
            self.set_error_message(str(e))
        finally:
            os.chdir(current_directory)
