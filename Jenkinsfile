def collection_path = 'ansible_collections/rudder/rudder'

// Do not use for the moment, do not store anything in clear text, to validate the way to store credentials.
// def galaxy_api_key = ''

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
    // stage ('publication on Galaxy') {
    //     agent {
    //         dockerfile {
    //             filename 'ci/ansible-galaxy.Dockerfile'
    //             additionalBuildArgs  '--build-arg USER_ID='+user_id
    //         }
    //     }
    //     steps {
    //         sh script: './ci/publisher.sh '+galaxy_api_key, label: 'publication on galaxy'
    //     }
    // }

    //stage ('role rudder_relay') {
    //  agent {
    //    image 'quay.io/ansible/toolset'
    //    args '-v /var/run/docker.sock:/var/run/docker.sock'
    //  }
    //  steps {
    //    sh './qa-test --rudder_relay'
    //  }
    //}
  }
}
