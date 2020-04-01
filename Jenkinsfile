pipeline {
  agent { label 'docker-slave' }
  stages {
    stage ('Pull repo code from github') {
      steps {
        checkout scm
      }
    }
    stage('test iac-blueprint-builder') {
        steps {
            sh "pip3 install -r requirements.txt"
            sh "pip3 install -e ."
            sh "pyttest"
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
