pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm  // pulls code from repo
            }
        }

        stage('Build and Dockerize') {
            steps {
                script {
                    sh 'docker stop $(docker ps -a -q)'  // stop any running containers 
                    sh 'docker system prune -f'  // remove existing containers
                    sh 'docker build -t dash-img .'
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    sh 'docker run -d --name dash-app -p 8050:8050 dash-img'  // create and start the container 
                }
            }
        }
    }
}
