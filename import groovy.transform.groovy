import groovy.transform.Field
def projectBranch = "master"
def projectURL = "ssh://git@tgcsgitlab.rtptgcs.com:20022/elevateNGP/elera-solution-test/tcxsky-ansible-tools.git"
@Field projectDir = "sample-project"
@Field inventoryPath = 'inventory/sample_inventory.yml'
@Field productVars = '../roles/tcxsky_copy_asm_transfer/vars/product.yml'
@Field varsDir = '../roles/tcxsky_copy_asm_transfer/vars'
@Field playbook = 'playbooks/elera/update-products.yml'
@Field finishInstallPlaybook = 'playbooks/elera/finish-install.yml'
@Field theComponents = ["ELERA core",
                        "ELERA Pay",
                        "ELERA EMA",
                        "TCx SDK"] as java.util.ArrayList
// @Field theComponents = ["ELERA core",
//                         "ELERA EMA",
//                         "TCx SDK"] as java.util.ArrayList
def productsDetails = [
    "ELERA core": [[name: "Admin UI", groupId: "com.tgcs.elera.client", artifactId: "elera-client-sky-adminui-zip", version: "",  productIds: "GQ", yamlVarsFile: "elera-admin-ui.yml"],
                   [name: "Device Broker for SDK", groupId: "com.tgcs.elera.client", artifactId: "elera-client-sky-device-broker-sdk-extension-zip", version: "", productIds: "CQ", yamlVarsFile: "device-broker-sdk-ext.yml"],
                   [name: "Terminal Services", groupId: "com.tgcs.elera.client", artifactId: "elera-client-sky-services-terminal-zip", version: "",  productIds: "FE", yamlVarsFile: "elera-terminal-services.yml"],
                   [name: "Client UI", groupId: "com.tgcs.elera.client", artifactId: "elera-client-sky-ui-controller-zip", version: "",  productIds: "FH", yamlVarsFile: "elera-ui.yml"],
                   [name: "Controller Services", groupId: "com.tgcs.elera.client", artifactId: "elera-client-sky-services-controller-zip", version: "",  productIds: "FP", yamlVarsFile: "elera-controller-services.yml"],
                   [name: "ELERA Platform", groupId: "com.tgcs.elera.client", artifactId: "elera-client-sky-lite-controller-zip", version: "",  productIds: "ES", yamlVarsFile: "elera-platform.yml"]],
    "ELERA Pay":  [[name: "ELERA Pay", groupId: "com.tgcs.tgp", artifactId: "elera-pay-install", version: "",  productIds: "FT", yamlVarsFile: "elera-pay.yml"]],
    "ELERA EMA":  [[name: "ELERA EMA UI", groupId: "com.tgcs.elera.client", artifactId: "elera-client-sky-emaui-zip", version: "", productIds: "QU", yamlVarsFile: "ema-ui.yml"]],
    "TCx SDK":    [[name: "TCx SDK", groupId: "com.tgcs.sdk.api", artifactId: "tcx-sdk-install-sky", version: "", productIds: "QR", yamlVarsFile: "tcx-sdk.yml"]]
]
@Field masterControllerIp = ""
@Field isInstallingSomething = false
@Field productNamesToInstall = ""
@Field productIdsToInstall = ""
@Field productsInstalled = ""
@Field emailContent = ""
def ansibleCommand(String playbookName) {
  def ret = "ansible-playbook -vvv playbooks/elera/${playbookName}.yml -e ansible_user=vxuser -i ${inventoryPath}"
  return ret
}
def runAnsibleCommand(String playbookName) {
    try {
        sh ansibleCommand(playbookName)
    } catch (ex) {
        updateEmailWithError("Exception caught from Ansible command:  '" + ex.getMessage() + "'")
        error(ex)
    }
}
def createProductYamlVars(Map productDetails) {
    println "Update vars for $productDetails.name"
    def yamlVars = readYaml file: productVars
    yamlVars.product_name = productDetails.name
    yamlVars.group_id = productDetails.groupId
    yamlVars.artifact_id = productDetails.artifactId
    yamlVars.product_id_list = productDetails.productIds
    yamlVars.level = productDetails.version
    writeYaml file: varsDir + '/' + productDetails.yamlVarsFile, data: yamlVars, overwrite: true
    println "Processed product: $productDetails"
}

def addProductToPlaybook(Map productDetails) {
    if (productDetails.version == null || productDetails.version.trim().isEmpty()) {
        return;
    }
    productNamesToInstall += ("'" +productDetails.name + "' ")
    productIdsToInstall += (productDetails.productIds + " ");
    // vars
    def installPlaybook = readYaml file: playbook
    def s = installPlaybook.size()
    println "The install playbook size is: $s"
    println "The playbook looks like: $installPlaybook"
    def newProduct = [:]
    newProduct.hosts = "mfs"
    newProduct.vars_files = []
    newProduct.vars_files[0] = "../../../roles/tcxsky_group_vars/controllers.yml"
    newProduct.vars_files[1] = productDetails.yamlVarsFile
    newProduct.roles = []
    newProduct.roles[0] = [role: "tcxsky_copy_asm_transfer"]
    installPlaybook[s] = newProduct;
    productsInstalled += "<tr><td>$productDetails.name</td><td><code>$productDetails.productIds</code></td><td>$productDetails.groupId<br/>$productDetails.artifactId</td><td>$productDetails.version</td></tr> "
    println "Meanwhile, the playbook looks like: $installPlaybook"
    installPlaybook[s].vars_files[1] = "../../../roles/tcxsky_copy_asm_transfer/vars/" + productDetails.yamlVarsFile
    s = installPlaybook.size()
    println "Now the install playbook size is: $s"
    println "All done, the playbook looks like: $installPlaybook"
    writeYaml file: playbook, data: installPlaybook, overwrite: true
    newProduct = [:];
    installPlaybook = [:];
}
def fetchIsosToProxyNexus(List productDetails) {
    productDetails.each { it -> 
        if (it.version != null && !it.version.isEmpty() ) {
            def artifactUrl = "http://tgcsnexus2.rtptgcs.com:28081/repository/tgcs-maven-group/${it.groupId.replace('.', '/')}/${it.artifactId}/${it.version}/${it.artifactId}-${it.version}.iso"
            println "Checking if ISO artifact $it.groupId:$it.artifactId:$it.version exists on Nexus."
            // Check if the artifact exists on proxy nexus (tgcsnexus2) and wait a maximum of 20 seconds on check
            def checkCmd = "curl --head --silent --fail --max-time 20 $artifactUrl"
            def artifactExists = sh(script: checkCmd, returnStatus: true) == 0
            if (artifactExists) {
                println "Artifact exists: $artifactUrl"
            } else {
                println "Artifact does not exist. Fetching ISO artifact $it.groupId:$it.artifactId:$it.version to cache on proxy nexus."
                sh "mvn dependency:get -DgroupId=$it.groupId -DartifactId=$it.artifactId -Dversion=$it.version -Dpackaging=iso -DremoteRepositories=http://tgcsnexus2.rtptgcs.com:28081/repository/tgcs-maven-group/"
            }
        }
    }
    println "Done fetching ISO artifacts for $productDetails"
}
def prepareProductForAsm(productTitle, product, parameters, globalFlagIndex) {
    println "Prepping install for $productTitle"
    def globalVersion = ""
    if (globalFlagIndex > -1) {
        globalVersion = parameters[globalFlagIndex];
    }
    // Reconcile the version of each product in a component.
    if (globalVersion) {
       product.eachWithIndex { it1, i -> it1["version"] = globalVersion }

    } 
    else {
        if (globalFlagIndex > -1) {
            product.eachWithIndex { it1, i -> it1["version"] = parameters[i + 1] }
        }
        else {
            product.eachWithIndex { it1, i -> it1["version"] = parameters[i] }
        }
    }
    println "Summary of versions for $productTitle"
    product.eachWithIndex{ it1, i -> println "$i : $it1";}
    product.eachWithIndex { it1, i -> println "Creating ansible vars file for: $it1.name"; 
                                      createProductYamlVars(it1); 
                                      addProductToPlaybook(it1); 
                                      println "Product IDs: $productIdsToInstall"; }
    // This should not be necessary.  All ELERA ISOs produced by elera-system are already pulled to the on-site proxy.  We can maybe add SDK.
    fetchIsosToProxyNexus(product)
    println "Preparation for $productTitle is complete."
}
def updateEmailWithError(String errorMessage) {
    emailContent += ('<br/><br/><h3>Error</h3>' + errorMessage + '<br/>')
}
def chmodPrivateKey() {
    sh "chmod 500 ${projectDir}/keys/vxuser_default_key"
}
pipeline {
    agent {
        label 'master'
    }
    tools {
        maven 'Maven-3.5.2'
        jdk 'jdk8'
    }
    options {
        timestamps()
    }
    post {
        always {
            script {
                echo 'Sending Build Status email to requestor...'
                wrap([$class: 'BuildUser']) {
                    emailext body: "${currentBuild.currentResult}: '${env.JOB_NAME}' completed.</br></br>The following were deployed to $masterControllerIp:${emailContent}</br></br>Job execution details: <a href='${env.BUILD_URL}'>${env.BUILD_URL}</a></br></br>",
                    subject: "Build ${currentBuild.currentResult}: ${env.JOB_NAME} to $masterControllerIp",
                    to: "${BUILD_USER_EMAIL}",
                    replyTo: 'tgcsdevadmin@toshibagcs.com'
                }
            }
        }
    }
    stages {
        stage('Parameters'){
            steps {
                script {
                    dir(projectDir) {
                        wrap([$class: 'BuildUser']) {
                            currentBuild.displayName += ": ${BUILD_USER} started deploy job"
                        }
                    }
                    properties([

                        parameters([
                            [$class: 'DynamicReferenceParameter',
                            choiceType: 'ET_FORMATTED_HTML',
                            description: 'IP address of Master Controller to install to.  It is required that the Master Controller have SSH enabled with a "vxuser" id configured for public key authentication.',
                            // filterLength: 1,
                            // filterable: false,
                            name: 'MFS_CONTROLLER_IP',
                            script: [
                                $class: 'GroovyScript',
                                fallbackScript: [
                                    classpath: [],
                                    sandbox: true,
                                    script:
                                        '''
                                        return '<p>Unable to display</p>'
                                        '''
                                    ],
                                script: [
                                    classpath: [],
                                    sandbox: true,
                                    script:
                                        '''
                                        return '<input name="value" value="" class="  " type="text">'
                                        '''
                                    ]
                                ]
                            ],
                            [$class: 'ChoiceParameter',
                            choiceType: 'PT_CHECKBOX',
                            description: '',
                            name: 'REBOOT_TERMINALS',
                            script: [
                                $class: 'GroovyScript',
                                fallbackScript: [
                                    classpath: [],
                                    sandbox: true,
                                    script:
                                        "return['Unable to display terminals to reboot.']"
                                    ],
                                script: [
                                    classpath: [],
                                    sandbox: true,
                                    script:
                                        '''
                                        return ['Reboot All Terminals?:selected']
                                        '''
                                    ]
                                ]
                            ],
                            // [$class: 'DynamicReferenceParameter',
                            // choiceType: 'ET_FORMATTED_HTML',
                            // description: 'Comma-separated list of terminals to reboot (i.e. 316,317)',
                            // name: 'TERMINALS',
                            // referencedParameters: 'REBOOT_TERMINALS',
                            // script:
                            //     [$class: 'GroovyScript',
                            //     fallbackScript: [
                            //         classpath: [],
                            //         sandbox: true,
                            //         script:
                            //             '''
                            //             return '<p>This is the fallback message for Terminal reboot.  Something bad happened.</p>'
                            //             '''
                            //         ],
                            //     script: [
                            //         classpath: [],
                            //         sandbox: true,
                            //         script:
                            //             '''
                            //             def htmlInputData = '<input name="value" value="" class="  " type="text">'

                            //             def htmlMessage = '<p><b>Terminal numbers</b> not selected for reboot.</p>'
                            //             if (REBOOT_TERMINALS.contains("Reboot All Terminals?")) {
                            //                 return htmlInputData
                            //             } else {
                            //                 return htmlMessage
                            //             }
                            //             '''
                            //         ]
                            //     ]
                            // ],
                            [$class: 'ChoiceParameter',
                            choiceType: 'PT_CHECKBOX',
                            description: 'Select components to install.  Multiple components can be installed.',
                            name: 'Components',
                            script: [
                                $class: 'GroovyScript',
                                fallbackScript: [
                                    classpath: [],
                                    sandbox: true,
                                    script:
                                        "return['Unable to display product component list for selecting deployments.']"
                                    ],
                                script: [
                                    classpath: [],
                                    sandbox: true,
                                    script:
                                        '''
                                        String theComponents = "ELERA core:selected, ELERA Pay:selected, ELERA EMA, TCx SDK"
                                        // String theComponents = "ELERA core, ELERA EMA, TCx SDK"
                                        def componentList = theComponents.trim().split(',').collect{ it.trim() }
                                        return componentList
                                        '''
                                    ]
                                ]
                            ],
                            [$class: 'DynamicReferenceParameter',
                            choiceType: 'ET_FORMATTED_HTML',
                            description: 'Enter the version of each ELERA core component to deploy or check the "Use common version for all base components" box if the version for all components is the same.',
                            name: 'ELERA_VERSION',
                            referencedParameters: 'Components',
                            script:
                                [$class: 'GroovyScript',
                                fallbackScript: [
                                    classpath: [],
                                    sandbox: true,
                                    script:
                                        '''
                                        return '<p>This is the fallback message for ELERA core components.  Something bad happened.</p>'
                                        '''
                                    ],
                                script: [
                                    classpath: [],
                                    sandbox: true,
                                    script:
                                        '''
                                        def htmlInputData = '<div>' +
                                            'Use <b>common version</b> for all base components&nbsp;<input name="value" value="" class="  " type="text"><br/><br/>' +
                                            '<table border="1" cellspacing="1" cellpadding="1"><tr><th>Component</th><th>Version</th></tr>' +
                                            '<tr><td>Admin UI - cash mgmt (<b>GQ</b>)</td><td><input name="value" value="" class="  " type="text"></td></tr>' +
                                            '<tr><td>Device Broker for SDK (<b>CQ</b>)</td><td><input name="value" value="" class="  " type="text"></td></tr>' +
                                            '<tr><td>Terminal Services (<b>FE</b>)</td><td><input name="value" value="" class="  " type="text"></td></tr>' +
                                            '<tr><td>Client UI (<b>FH</b>)</td><td><input name="value" value="" class="  " type="text"></td></tr>' +
                                            '<tr><td>Controller Services (<b>FP</b>)</td><td><input name="value" value="" class="  " type="text"></td></tr>' +
                                            '<tr><td>Platform (<b>ES</b>)</td><td><input name="value" value="" class="  " type="text"></td></tr>' +
                                            '</table>' +
                                            '</div>'
                                        def htmlMessage = '<p><b>ELERA core</b> not selected for deployment.</p>'
                                        def componentList = Components.split(',').collect{ it.trim() }
                                        if (componentList.contains("ELERA core")) {
                                            return htmlInputData

                                        } else {
                                            return htmlMessage
                                        }
                                        '''
                                    ]
                                ]
                            ],
                            [$class: 'DynamicReferenceParameter',
                            choiceType: 'ET_FORMATTED_HTML',
                            description: 'ELERA Pay version to deploy.',
                            name: 'ELERA_PAY_VERSION',
                            referencedParameters: 'Components',
                            script:
                                [$class: 'GroovyScript',
                                fallbackScript: [
                                    classpath: [],
                                    sandbox: true,
                                    script:
                                        '''
                                        return '<p>This is the fallback message for ELERA Pay.  Something bad happened.</p>'
                                        '''
                                    ],
                                script: [
                                    classpath: [],
                                    sandbox: true,
                                    script:
                                        '''
                                        def htmlInputData = '<input name="value" value="" class="  " type="text">'
                                        def htmlMessage = '<p><b>ELERA Pay</b> not selected for deployment.</p>'
                                        def componentList = Components.split(',').collect{ it.trim() }
                                        if (componentList.contains("ELERA Pay")) {
                                            return htmlInputData
                                        } else {
                                            return htmlMessage
                                        }
                                        '''
                                    ]
                                ]
                            ],
                            [$class: 'DynamicReferenceParameter',
                            choiceType: 'ET_FORMATTED_HTML',
                            description: 'ELERA EMA version to deploy',
                            name: 'ELERA_EMA_VERSION',
                            referencedParameters: 'Components',
                            script:
                                [$class: 'GroovyScript',
                                fallbackScript: [
                                    classpath: [],
                                    sandbox: true,
                                    script:
                                        '''
                                        return '<p>This is the fallback message for ELERA EMA.  Something bad happened.</p>'
                                        '''
                                    ],
                                script: [
                                    classpath: [],
                                    sandbox: true,
                                    script:
                                        '''
                                        def htmlInputData = '<input name="value" value="" class="  " type="text">'
                                        def htmlMessage = '<p><b>ELERA EMA</b> not selected for deployment.</p>'
                                        def componentList = Components.split(',').collect{ it.trim() }
                                        if (componentList.contains("ELERA EMA")) {
                                            return htmlInputData
                                        } else {
                                            return htmlMessage
                                        }
                                        '''
                                    ]
                                ]

                            ],
                            [$class: 'DynamicReferenceParameter',
                            choiceType: 'ET_FORMATTED_HTML',
                            description: 'TCx SDK version to deploy.',
                            name: 'TCX_SDK_VERSION',
                            referencedParameters: 'Components',
                            script:
                                [$class: 'GroovyScript',
                                fallbackScript: [
                                    classpath: [],
                                    sandbox: true,
                                    script:
                                        '''
                                        return '<p>This is the fallback message for TCx SDK.  Something bad happened.</p>'
                                        '''
                                    ],
                                script: [
                                    classpath: [],
                                    sandbox: true,
                                    script:
                                        '''
                                        def htmlInputData = '<input name="value" value="" class="  " type="text">'
                                        def htmlMessage = '<p><b>TCx SDK</b> not selected for deployment.</p>'
                                        def componentList = Components.split(',').collect{ it.trim() }
                                        if (componentList.contains("TCx SDK")) {
                                            return htmlInputData
                                        } else {
                                            return htmlMessage
                                        }
                                        '''
                                    ]
                                ]
                            ]
                        ])
                    ])
                }
            }
        }

        stage('Check Out') {
            steps {
                echo "Entered text: ${ELERA_VERSION}"
                echo "Install to: ${MFS_CONTROLLER_IP}"
                script {
                    cleanWs disableDeferredWipeout: true, deleteDirs: true
                    git credentialsId: 'jenkins-gitlab-ssh',
                        url: projectURL,
                        branch: projectBranch
                    chmodPrivateKey()
                }
            }
        }

        stage('Update Store IPs') {
            steps {
                script {

                    if (!MFS_CONTROLLER_IP || MFS_CONTROLLER_IP == ",") { 
                        String msg = 'An IP address of a Master Controller must be specified!';
                        updateEmailWithError(msg); 
                        error(msg);
                    }
                    def masterIpAddress = MFS_CONTROLLER_IP.split(',');

                    dir(projectDir) {
                        masterControllerIp = masterIpAddress[0].trim();
                        wrap([$class: 'BuildUser']) {
                            currentBuild.displayName += " to ${masterControllerIp}"
                        }
                        def inventoryFile = readYaml file: inventoryPath

                        inventoryFile.all.children.controllers.children.mfs.hosts = masterControllerIp
                        writeYaml file: inventoryPath, data: inventoryFile, overwrite: true
                    }
                }
            }
        }

        stage('Do deploys') {
            steps {
                
                script {

                    // TERMINALS = TERMINALS.trim()
                    def terminals_rebooted = 'False'
                    println "REBOOT_TERMINALS: ${REBOOT_TERMINALS}"
                    if (REBOOT_TERMINALS.contains("Reboot All Terminals?")) {
                        terminals_rebooted = 'True'
                    }
                    ELERA_VERSION = ELERA_VERSION.trim()
                    ELERA_PAY_VERSION = ELERA_PAY_VERSION.trim()
                    TCX_SDK_VERSION = TCX_SDK_VERSION.trim()

                    println "Parameters:"
                    println "  Install to IP: $masterControllerIp"
                    println "  All Terminals to be rebooted: ${terminals_rebooted}"
                    println "  Components: $Components"
                    println "  ELERA_VERSION:  >${ELERA_VERSION}<"
                    println "  ELERA_PAY_VERSION:  >${ELERA_PAY_VERSION}<"
                    println "  ELERA_EMA_VERSION:  >${ELERA_EMA_VERSION}<"
                    println "  TCX_SDK_VERSION:  >${TCX_SDK_VERSION}<"

                    dir(projectDir) {
                        if (!ELERA_VERSION.isEmpty() && !ELERA_VERSION.replaceAll(",", "").isEmpty()) {

                            isInstallingSomething = true

                            def product = productsDetails["ELERA core"]
                            def parameters = ELERA_VERSION.trim().split(',').collect{ it.trim() }
                            prepareProductForAsm("ELERA core", product, parameters, 0)
                        }

                        if (!ELERA_PAY_VERSION.isEmpty() && !ELERA_PAY_VERSION.replaceAll(",", "").isEmpty()) {

                            isInstallingSomething = true

                            def product = productsDetails["ELERA Pay"]
                            def parameters = ELERA_PAY_VERSION.trim().split(',').collect { it.trim() }
                            prepareProductForAsm("ELERA Pay", product, parameters, -1)
                        }

                        if (!ELERA_EMA_VERSION.isEmpty() && !ELERA_EMA_VERSION.replaceAll(",", "").isEmpty()) {

                            isInstallingSomething = true

                            def product = productsDetails["ELERA EMA"]
                            def parameters = ELERA_EMA_VERSION.trim().split(',').collect { it.trim() }
                            prepareProductForAsm("ELERA EMA", product, parameters, -1)
                        }

                        if (!TCX_SDK_VERSION.isEmpty() && !TCX_SDK_VERSION.replaceAll(",", "").isEmpty()) {

                            isInstallingSomething = true

                            def product = productsDetails["TCx SDK"]
                            def parameters = TCX_SDK_VERSION.trim().split(',').collect { it.trim() }
                            prepareProductForAsm("TCx SDK", product, parameters, -1)
                        }

                        if (isInstallingSomething) {
                                // remove template product from playbook

                                def installPlaybook = readYaml file: playbook
                                installPlaybook.remove(0);
                                writeYaml file: playbook, data: installPlaybook, overwrite: true

                                // ASM all product specified
                                runAnsibleCommand('update-products')
                        }
                        else {
                            String msg = 'No components were selected to install or version information is missing.';
                            updateEmailWithError(msg);
                            error(msg);
                        }
                    }
                }
            }
        }
        stage('Finish Install') {
            steps {
                echo "Finish install on : $masterControllerIp"
                script {

                    dir(projectDir) {
                        def finishScript = readYaml file: finishInstallPlaybook
                        finishScript[0].tasks[0].vars.product_id_list = productIdsToInstall
                        finishScript[0].tasks[0].vars.product_name = productNamesToInstall
                        finishScript[0].tasks[0].vars.module_level_report_qualifier = 'DynISSDeploy'
                        def terminalRebootInfo = '<br/><br/>No terminals set to be rebooted.'
                        if (REBOOT_TERMINALS.contains("Reboot All Terminals?")) {
                            println "All terminals should be rebooted"
                            // def terminalList = TERMINALS.trim().split(",").collect { it.trim() }
                            // println "Terminal list: $terminalList"
                            // String terminalString = terminalList.join(",")
                            // println "Terminal string: $terminalString"
                            terminalRebootInfo = ('<br/><br/>All terminals set to be rebooted.')
                            finishScript[0].tasks[0].vars.terminals = '0'; // 0 = reboot all terminals
                        }

                        writeYaml file: finishInstallPlaybook, data: finishScript, overwrite: true

                        println "This is the finish playbook: $finishScript"
                        runAnsibleCommand('finish-install')

                        emailContent += ('<br/><br/><table border="1" cellspacing="1" cellpadding="1"><tr><th>Product Name</th><th>Product IDs</th><th>Artifact</th><th>Version</th></tr>' + productsInstalled + '</table>')

                        def reportModuleData = readFile(file: '../roles/tcxsky_report_module_level/reports/DynISSDeploy-adxcssdf.dat')

                        println "Straight from the file we have: >$reportModuleData<"
                        def reportModuleLevelLines = reportModuleData.split('\n')

                        String reportModuleLevelOutput = ""

                        for (int i = 0; i < reportModuleLevelLines.size(); i++) {
                            reportModuleLevelOutput += ('<code>' +
                                                        reportModuleLevelLines[i].substring(0, reportModuleLevelLines[i].length()-1) +
                                                        '</code><br/>')
                        }

                        emailContent += ('<br/><br/><pre>' + reportModuleLevelOutput + '</pre>' + terminalRebootInfo)
                        println "emailContent: $emailContent"
                    }
                }
            }
        }
    }
}
