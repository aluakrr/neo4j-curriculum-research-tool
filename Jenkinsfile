pipeline {
    agent any
    options {
        timestamps()
        disableConcurrentBuilds()
        skipStagesAfterUnstable()
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }
    triggers { pollSCM('* * * * *') }
    parameters {
        booleanParam(name: 'PUSH_DOCKER_HUB', defaultValue: false,
                     description: 'Requires dockerhub credentials and an owned Docker Hub namespace.')
        string(name: 'DOCKERHUB_NAMESPACE', defaultValue: '', description: 'Your Docker Hub username')
        booleanParam(name: 'DEPLOY_TEST', defaultValue: true,
                     description: 'Run the tested image on the local Docker test host and archive results.')
    }
    stages {
        stage('Prepare') {
            steps {
                script {
                    env.REVISION = sh(script: 'git rev-parse --short=12 HEAD', returnStdout: true).trim()
                    env.APP_IMAGE = "curriculum-graph:${env.REVISION}"
                    env.TEST_IMAGE = "curriculum-graph-tests:${env.REVISION}"
                    env.RUN_NAME = "curriculum-ci-${env.BUILD_NUMBER}"
                }
                sh 'mkdir -p reports; git rev-parse HEAD > reports/commit.txt; docker version > reports/docker-version.txt'
            }
        }
        stage('Unit tests') {
            steps {
                sh '''
                    docker build --target test -t "$TEST_IMAGE" .
                    docker run --rm "$TEST_IMAGE" python -m ruff check src tests ci
                    docker create --name "$RUN_NAME" "$TEST_IMAGE" python -m pytest tests --junitxml=/tmp/junit.xml
                    set +e
                    docker start -a "$RUN_NAME"
                    result=$?
                    docker cp "$RUN_NAME":/tmp/junit.xml reports/junit.xml
                    copied=$?
                    docker rm "$RUN_NAME"
                    if [ "$copied" -ne 0 ]; then exit "$copied"; fi
                    exit "$result"
                '''
            }
            post { always { junit testResults: 'reports/junit.xml', allowEmptyResults: false } }
        }
        stage('Build Docker image') {
            steps {
                sh '''
                    docker build --target runtime --label org.opencontainers.image.revision="$GIT_COMMIT" -t "$APP_IMAGE" .
                    docker image inspect "$APP_IMAGE" > reports/image.json
                    docker run --rm --entrypoint python "$APP_IMAGE" --version > reports/python-version.txt
                '''
            }
        }
        stage('Smoke test image') {
            steps {
                sh '''
                    docker run --rm "$APP_IMAGE" > reports/stats.json
                    docker run --rm "$APP_IMAGE" data/sample_curriculum.json score AI301 --completed CS101 CS201 > reports/score.json
                    docker run --rm "$APP_IMAGE" data/sample_curriculum.json available --completed CS101 CS201 > reports/available.json
                    docker run --rm "$APP_IMAGE" data/sample_curriculum.json cypher > reports/import.cypher
                    docker run --rm "$APP_IMAGE" data/sample_curriculum.json cypher > reports/import-repeat.cypher
                    docker create --name "$RUN_NAME" -e GIT_COMMIT="$GIT_COMMIT" "$TEST_IMAGE" python ci/smoke.py
                    docker cp reports/. "$RUN_NAME":/evidence
                    set +e
                    docker start -a "$RUN_NAME" > reports/smoke.json
                    result=$?
                    docker rm "$RUN_NAME"
                    cat reports/smoke.json
                    exit "$result"
                '''
            }
        }
        stage('Push to Docker Hub (optional)') {
            when { expression { params.PUSH_DOCKER_HUB } }
            steps {
                script {
                    if (!(params.DOCKERHUB_NAMESPACE ==~ /[a-z0-9][a-z0-9_-]{1,38}/)) {
                        error('Provide a valid Docker Hub namespace.')
                    }
                }
                withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'HUB_USER', passwordVariable: 'HUB_TOKEN')]) {
                    sh '''
                        set +x
                        export DOCKER_CONFIG=$(mktemp -d)
                        trap 'rm -rf "$DOCKER_CONFIG"' EXIT
                        printf '%s' "$HUB_TOKEN" | docker login --username "$HUB_USER" --password-stdin
                        docker tag "$APP_IMAGE" "$DOCKERHUB_NAMESPACE/curriculum-graph:$REVISION"
                        docker push "$DOCKERHUB_NAMESPACE/curriculum-graph:$REVISION"
                    '''
                }
            }
        }
        stage('Deploy to test environment') {
            when { expression { params.DEPLOY_TEST } }
            steps {
                sh '''
                    docker create --name "$RUN_NAME" --label environment=test "$APP_IMAGE" data/sample_curriculum.json cypher
                    set +e
                    docker start -a "$RUN_NAME" > reports/deployed-import.cypher
                    result=$?
                    docker inspect "$RUN_NAME" > reports/deployment.json
                    docker rm "$RUN_NAME"
                    if [ "$result" -ne 0 ]; then exit "$result"; fi
                    cmp reports/import.cypher reports/deployed-import.cypher
                    echo 'Test deployment completed; generated Cypher matches the smoke-tested artifact.'
                '''
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'reports/**', fingerprint: true, allowEmptyArchive: true
            sh 'if [ -n "$RUN_NAME" ]; then docker rm -f "$RUN_NAME" >/dev/null 2>&1 || true; fi'
        }
    }
}
