pipeline {

    agent {
        node {
            label 'docker_linux'
        }
    }

    parameters {
        string(name: 'PLUGIN',
                defaultValue: 'release-terraform-integration',
                description: 'Name of the Container Plugin to be build')
        string(name: 'VERSION', defaultValue: '', description: 'Release version number for artifacts')
        string(name: 'REGISTRY_ORG', defaultValue: 'xebialabsunsupported', description: 'docker repo')
        string(name: 'RELEASE_BRANCH_NAME', defaultValue: '', description: 'release branch to be build')
    }

    environment {
        NEXUS_CRED = credentials('nexus-ci')
        PLUGIN = "${params.PLUGIN}"
        VERSION = "${params.VERSION}"
        REGISTRY_URL = "docker.io"
        REGISTRY_ORG = "${params.REGISTRY_ORG}"
    }

    stages {
        stage('Environment Setup') {
            steps {
                echo 'Setting up project.properties'
                echo "$params.PLUGIN"
                echo "$params.VERSION"
                echo "$params.REGISTRY_URL"
                sh "cat > project.properties <<EOF\nPLUGIN=${params.PLUGIN}\nVERSION=${params.VERSION}\nEOF\n"
            }
        }

        stage('Build Zip') {
            steps {
                echo 'Building the plugin zip'
                sh "chmod +x build.sh"
                //sh "ls -lrth"
                sh "./build.sh --zip"
            }
        }

        stage('Build zip sha1') {
            steps {
                echo 'Building the plugin sha1 file'

                sh "sha1sum build/${params.PLUGIN}-${params.VERSION}.zip | cut -d ' ' -f 1 | tr -d '\n' > build/${params.PLUGIN}-${params.VERSION}.zip.sha1"

                sh 'curl -v -u $NEXUS_CRED_USR:$NEXUS_CRED_PSW --upload-file build/$PLUGIN-$VERSION.zip.sha1 https://nexus.xebialabs.com/nexus/content/repositories/releases/com/xebialabs/xlrelease/plugins/$PLUGIN/$VERSION/$PLUGIN-$VERSION.zip.sha1'
            }
        }

        stage('Build Pom') {
            steps {
                echo 'Building the plugin pom'

                sh "mvn -B archetype:generate -DgroupId=com.xebialabs.xlrelease.plugins -DartifactId=${params.PLUGIN} -DarchetypeArtifactId=maven-archetype-quickstart -DinteractiveMode=false -Dversion=${params.VERSION} -DskipTests=true"
                sh "ls"
                echo "........................"
                sh "cd  ${params.PLUGIN}"
                sh "ls"


                sh 'curl -v -u $NEXUS_CRED_USR:$NEXUS_CRED_PSW --upload-file $PLUGIN/pom.xml https://nexus.xebialabs.com/nexus/content/repositories/releases/com/xebialabs/xlrelease/plugins/$PLUGIN/$VERSION/$PLUGIN-$VERSION.pom'
            }
        }

        stage('Build pom sha1') {
            steps {
                echo 'Building the pom sha1 file'

                sh "sha1sum ${params.PLUGIN}/pom.xml | cut -d ' ' -f 1 | tr -d '\n' > ${params.PLUGIN}/${params.PLUGIN}-${params.VERSION}.pom.sha1"

                sh 'curl -v -u $NEXUS_CRED_USR:$NEXUS_CRED_PSW --upload-file $PLUGIN/$PLUGIN-$VERSION.pom.sha1 https://nexus.xebialabs.com/nexus/content/repositories/releases/com/xebialabs/xlrelease/plugins/$PLUGIN/$VERSION/$PLUGIN-$VERSION.pom.sha1'
            }
        }

        stage('Upload Build Zip to nexus') {
            steps {

                sh 'curl -v -u $NEXUS_CRED_USR:$NEXUS_CRED_PSW --upload-file build/$PLUGIN-$VERSION.zip https://nexus.xebialabs.com/nexus/content/repositories/releases/com/xebialabs/xlrelease/plugins/$PLUGIN/$VERSION/$PLUGIN-$VERSION.zip'

                echo 'Successfully uploaded plugin to Nexus!'
            }
        }

        stage('Docker build and push') {
            steps {
                echo 'Docker build and docker push'
                sh "./build.sh --image"
                cleanWs()
            }
        }
    }
}
