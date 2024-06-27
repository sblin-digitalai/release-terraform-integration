import ast
import json
import os
import subprocess
import uuid
from digitalai.release.integration import BaseTask


class Apply(BaseTask):

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
            ssh_keys = self.input_properties['sshKeys']
            known_hosts = self.input_properties['knownHosts']

            try:
                if ssh_keys:
                    dir = os.path.expanduser('~') + "/.ssh"
                    path = f"{dir}/id_rsa"
                    if not os.path.isdir(dir):
                        os.mkdir(dir)
                    file = open(path, "w")
                    file.write(ssh_keys)
                    file.write(os.linesep)
                    file.close()
                    os.chmod(path,0o400)
            except Exception as e:
                raise Exception(f"Error: {e}")
            
            try:
                if known_hosts:
                    dir = os.path.expanduser('~') + "/.ssh"
                    path = f"{dir}/known_hosts"
                    if not os.path.isdir(dir):
                        os.mkdir(dir)
                    file = open(path, "w")
                    file.write(known_hosts)
                    file.close()
                    os.chmod(path,0o400)
            except Exception as e:
                raise Exception(f"Error: {e}")

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
                raise Exception(f"Git clone command failed: For more information, please check the 'View logs' section")

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
                raise Exception("Init command failed: : For more information, please check the 'View logs' section")

            apply_process = subprocess.run(["terraform", "apply", "-auto-approve"], env=env_vars, text=True)
            if apply_process.returncode != 0:
                raise Exception("Apply command failed: : For more information, please check the 'View logs' section")

            output_process = subprocess.run(["terraform", "output", "-json"], capture_output=True, env=env_vars, text=True)
            if output_process.returncode != 0:
                raise Exception(f"Output command failed: {output_process.stderr}")

            output_json = json.loads(output_process.stdout)
            output_variables = {}
            for key, value in output_json.items():
                output_variables[key] = value["value"]

            if output_variables:
                self.set_output_property('outputVariables', output_variables)
                self.add_comment(str(output_variables))

            # Remove environment variables from os.environ
            for key in environment_variables:
                os.environ.pop(key, None)

            # Remove the id_rsa file
            if os.path.isfile("~/.ssh/id_rsa"):
                try:
                    os.remove("~/.ssh/id_rsa")
                    os.rmdir("~/.ssh")
                except Exception as e:
                    print("Exception {e}")

        except Exception as e:
            self.set_exit_code(1)
            self.set_error_message(str(e))
        finally:
            os.chdir(current_directory)
