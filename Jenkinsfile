pipeline {
agent { label 'docker-slave' }
       environment {
       docker_registry_ip = credentials('jenkins-docker-registry-ip')
    }
    stages {
        stage ('Pull repo code from github') {
            steps {
                checkout scm
            }
        }
        stage('build and push docker image') {
                steps {
                    sh "docker build -t iac-blueprint-builder ."
                    sh "docker tag iac-blueprint-builder $docker_registry_ip/iac-blueprint-builder"
                    sh "docker push $docker_registry_ip/iac-blueprint-builder"
                }
        }
        stage('Push Docker image to DockerHub') {
                when {
                    branch 'master'
                }
                steps {
                    withDockerRegistry(credentialsId: 'jenkins-sodalite.docker_token', url: '') {
                        sh  """#!/bin/bash                       
                                docker tag iac-blueprint-builder sodaliteh2020/iac-blueprint-builder:${BUILD_NUMBER}
                                docker tag iac-blueprint-builder sodaliteh2020/iac-blueprint-builder
                                docker push sodaliteh2020/iac-blueprint-builder:${BUILD_NUMBER}
                                docker push sodaliteh2020/iac-blueprint-builder
                            """
                    }
                }
        }
        stage('test iac-blueprint-builder') {
                steps {
                    sh  """ #!/bin/bash 
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
