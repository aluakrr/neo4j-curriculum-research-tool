pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        TEST_IMAGE = "neo4j-curriculum-research-tool:test-${BUILD_NUMBER}"
        RUNTIME_IMAGE = "neo4j-curriculum-research-tool:${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Test Image') {
            steps {
                sh 'docker build --target test -t "$TEST_IMAGE" .'
            }
        }

        stage('Compile Lint and Test') {
            steps {
                sh "docker run --rm --entrypoint sh \"$TEST_IMAGE\" -c 'python -m compileall -q src && ruff check src tests && pytest'"
            }
        }

        stage('Build Runtime Image') {
            steps {
                sh 'docker build --target runtime -t "$RUNTIME_IMAGE" .'
            }
        }

        stage('Container Smoke Test') {
            steps {
                sh 'docker run --rm "$RUNTIME_IMAGE"'
            }
        }
    }

    post {
        always {
            sh 'docker image rm -f "$TEST_IMAGE" "$RUNTIME_IMAGE" || true'
            deleteDir()
        }
    }
}
