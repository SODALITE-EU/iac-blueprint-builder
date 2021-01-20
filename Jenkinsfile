pipeline {
agent { label 'docker-slave' }
       environment {
       // OPENSTACK SETTINGS
       ssh_key_name = "jenkins-opera"
       image_name = "centos7"
       network_name = "orchestrator-network"
       security_groups = "default,sodalite-remote-access,sodalite-rest,sodalite-uc"
       flavor_name = "m1.medium"
       // DOCKER SETTINGS
       docker_network = "sodalite"
       docker_registry_ip = credentials('jenkins-docker-registry-ip')
       docker_public_registry_url = "registry.hub.docker.com"
       xopera_endpoint = "http://192.168.2.26:5000/""

       // CI-CD vars
       // When triggered from git tag, $BRANCH_NAME is actually GIT's tag_name
       TAG_SEM_VER_COMPLIANT = """${sh(
                returnStdout: true,
                script: './validate_tag.sh SemVar $BRANCH_NAME'
            )}"""

       TAG_MAJOR_RELEASE = """${sh(
                returnStdout: true,
                script: './validate_tag.sh MajRel $BRANCH_NAME'
            )}"""

       TAG_PRODUCTION = """${sh(
                returnStdout: true,
                script: './validate_tag.sh production $BRANCH_NAME'
            )}"""

       TAG_STAGING = """${sh(
                returnStdout: true,
                script: './validate_tag.sh staging $BRANCH_NAME'
            )}"""
    }
    stages {
        stage ('Pull repo code from github') {
            steps {
                checkout scm
            }
        }
        stage('Inspect GIT TAG'){
            steps {
                sh """ #!/bin/bash
                echo 'TAG: $BRANCH_NAME'
                echo 'Tag is compliant with SemVar 2.0.0: $TAG_SEM_VER_COMPLIANT'
                echo 'Tag is Major release: $TAG_MAJOR_RELEASE'
                echo 'Tag is production: $TAG_PRODUCTION'
                echo 'Tag is staging: $TAG_STAGING'
                """
            }

        }
        stage('test iac-blueprint-builder') {
                steps {
                    sh  """ #!/bin/bash
                            python3 -m venv venv-test
                            . venv-test/bin/activate
                            pip3 install -r requirements.txt
                            pip3 install -e .
                            python3 -m pytest --pyargs -s ${WORKSPACE}/test --junitxml="results.xml" --cov=src --cov-report xml test/
                        """
                    junit 'results.xml'
                }
        }
        stage('SonarQube analysis'){
                environment {
                scannerHome = tool 'SonarQubeScanner'
                }
                steps {
                    withSonarQubeEnv('SonarCloud') {
                            sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
        }
        stage('Build iac-blueprint-builder') {
            when {
                allOf {
                    // Triggered on every tag, that is considered for staging or production
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true' || TAG_PRODUCTION == 'true'
                    }
                }
            }
            steps {
                sh """#!/bin/bash
                    ./make_docker.sh build iac-blueprint-builder
                    """
            }
        }
        stage('Push iac-blueprint-builder to sodalite-private-registry') {
            // Push during staging and production
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true' || TAG_PRODUCTION == 'true'
                    }
                }
            }
            steps {
                withDockerRegistry(credentialsId: 'jenkins-sodalite.docker_token', url: '') {
                    sh  """#!/bin/bash
                        ./make_docker.sh push iac-blueprint-builder staging
                        """
                }
            }
        }
        stage('Push iac-blueprint-builder to DockerHub') {
            // Only on production tags
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_PRODUCTION == 'true'
                    }
                }
            }
            steps {
                withDockerRegistry(credentialsId: 'jenkins-sodalite.docker_token', url: '') {
                    sh  """#!/bin/bash
                            ./make_docker.sh push iac-blueprint-builder production
                        """
                }
            }
            stage('Install deploy dependencies') {
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true' || TAG_PRODUCTION == 'true'
                    }
                }
            }
            steps {
                sh """#!/bin/bash
                    python3 -m venv venv-deploy
                    . venv-deploy/bin/activate
                    python3 -m pip install --upgrade pip
                    python3 -m pip install opera[openstack]==0.6.2 docker
                    ansible-galaxy install geerlingguy.pip,2.0.0 --force
                    ansible-galaxy install geerlingguy.docker,2.9.0 --force
                    ansible-galaxy install geerlingguy.repo-epel,3.0.0 --force
                    rm -r -f openstack-blueprint/modules/
                    git clone -b 3.1.0 https://github.com/SODALITE-EU/iac-modules.git openstack-blueprint/modules/
                   """
            }
        }
        stage('Deploy to openstack for staging') {
            // Only on staging tags
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true'
                    }
                }
            }
            environment {
                // add env var for this stage only
                vm_name = 'iac-blueprint-builder-dev'
            }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'xOpera_ssh_key', keyFileVariable: 'xOpera_ssh_key_file', usernameVariable: 'xOpera_ssh_username')]) {
                    sh """#!/bin/bash
                        # create input.yaml file from template
                        envsubst < openstack-blueprint/input.yaml.tmpl > openstack-blueprint/input.yaml
                        . venv-deploy/bin/activate
                        cd openstack-blueprint
                        rm -r -f .opera
                        opera deploy service.yaml -i input.yaml
                       """
                }
            }
        }
        stage('Deploy to openstack for production') {
            // Only on production tags
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_PRODUCTION == 'true'
                    }
                }
            }
            environment {
                vm_name = 'iac-blueprint-builder'
            }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'xOpera_ssh_key', keyFileVariable: 'xOpera_ssh_key_file', usernameVariable: 'xOpera_ssh_username')]) {
                    sh """#!/bin/bash
                        # create input.yaml file from template
                        envsubst < openstack-blueprint/input.yaml.tmpl > openstack-blueprint/input.yaml
                        . venv-deploy/bin/activate
                        cd openstack-blueprint
                        rm -r -f .opera
                        opera deploy service.yaml -i input.yaml
                       """
                }
            }
        }
        }
  }
  post {
	  failure {
	      slackSend (color: '#FF0000', message: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
	  }
	  fixed {
	      slackSend (color: '#6d3be3', message: "FIXED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
	  }
	}
}
