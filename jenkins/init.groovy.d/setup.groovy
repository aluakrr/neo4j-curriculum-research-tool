import jenkins.model.Jenkins
import hudson.security.HudsonPrivateSecurityRealm
import hudson.security.FullControlOnceLoggedInAuthorizationStrategy
import hudson.plugins.git.GitSCM
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition

def instance = Jenkins.get()
def realm = new HudsonPrivateSecurityRealm(false)
realm.createAccount('admin', System.getenv('JENKINS_ADMIN_PASSWORD'))
instance.setSecurityRealm(realm)
def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
// Anonymous viewers may inspect evidence; only the local administrator can change or run jobs.
strategy.setAllowAnonymousRead(true)
instance.setAuthorizationStrategy(strategy)
instance.setNumExecutors(1)
instance.setSystemMessage('Assignment 5 | Alua Koishybay | Neo4j Curriculum Research Tool')
def name = 'curriculum-research-ci'
if (instance.getItem(name) == null) {
    def job = instance.createProject(WorkflowJob, name)
    def scm = new GitSCM(System.getenv('REPOSITORY_URL'))
    scm.branches = [new hudson.plugins.git.BranchSpec('*/' + System.getenv('REPOSITORY_BRANCH'))]
    def definition = new CpsScmFlowDefinition(scm, 'Jenkinsfile')
    definition.setLightweight(true)
    job.setDefinition(definition)
    job.setDescription('Tests, container build, research smoke checks, and local test deployment. SCM polled every minute.')
    job.save()
}
instance.save()
