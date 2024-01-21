pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and Dockerize') {
            steps {
                script {
                    // Build and Dockerize your Dash app
                    sh 'docker system prune -f'
                    sh 'docker build -t dash-img .'
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    // Push the Docker image to your Docker registry or deploy it directly
                    sh 'docker run -d --name dash-app -p 8050:8050 dash-img'
                }
            }
        }
    }
}
