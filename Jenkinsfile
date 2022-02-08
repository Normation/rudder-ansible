// uid of the jenkins user of the docker runners
def user_id = "1007"

pipeline {
  agent none
  stages {
    stage ('typos') {
        agent {
            dockerfile {
                filename 'ci/typos.Dockerfile'
                additionalBuildArgs  '--build-arg VERSION=1.0'
            }
        }
        steps {
            sh script: './qa-test --typos', label: 'check collection typos'
        }
    }
    stage ('ansible sanity tests') {
        agent {
            dockerfile {
                filename 'ci/ansible-test.Dockerfile'
                additionalBuildArgs  '--build-arg USER_ID='+user_id
            }
        }
        steps {
            sh script: 'pwd'
            sh script: 'ansible-test sanity', label: 'ansible sanity checks'
        }
    }
    stage ('ansible unit tests') {
        agent {
            dockerfile {
                filename 'ci/ansible-test.Dockerfile'
                additionalBuildArgs  '--build-arg USER_ID='+user_id
            }
        }
        steps {
            sh script: './qa-test --unit-tests', label: 'ansible unit checks'
        }
    }
  }
}
