import requests
import json
import logging

logger = logging.getLogger()
logger.disabled = True


def get_title(id):
    titles = [
        'Adding a mobile front - end to a legacy app',
        'Advanced Analytics Architecture',
        'Anomaly Detector Process',
        'Archive on - premises data to cloud',
        'Build web and mobile applications',
        'Container CI / CD using Jenkins and Kubernetes on Azure Kubernetes Service(AKS)',
        'Custom Data Sovereignty \\& Data Gravity Requirements',
        'Defect prevention with predictive maintenance',
        'Demand Forecasting + Price Optimization',
        'Design Review Powered by Mixed Reality',
        'DevTest Image Factory',
        'Discovery Hub with Cloud Scale Analytics',
        'Enterprise-scale disaster recovery',
        'HPC System and Big Compute Solutions',
        'Hybrid ETL with Azure Data Factory',
        'Loan Credit Risk + Default Modeling',
        'Master Data Management powered by CluedIn',
        'Modern Data Warehouse Architecture',
        'Personalized marketing solutions',
        'Predicting Length of Stay in Hospitals',
        'Predictive Aircraft Engine Monitoring',
        'Predictive Insights with Vehicle Telematics',
        'Quality Assurance',
        'Real Time Analytics on Big Data Architecture',
        'Retail and e-commerce using Cosmos DB',
        'Sharing location in real time using low-cost serverless Azure services',
        'SMB disaster recovery with Azure Site Recovery',
        'SMB disaster recovery with Double-Take DR',
        'Speech Services',
        'Tier Applications & Data for Analytics',
        'Unlock Legacy Data with Azure Stack'
    ]
    return titles[id]

def get_sources(id):
    sources = [
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/adding-a-modern-web-and-mobile-frontend-to-a-legacy-claims-processing-application',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/advanced-analytics-on-big-data',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/anomaly-detector-process',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/backup-archive-on-premises',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/webapps',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/container-cicd-using-jenkins-and-kubernetes-on-azure-container-service',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/data-sovereignty-and-gravity',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/defect-prevention-with-predictive-maintenance',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/demand-forecasting-price-optimization-marketing',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/collaborative-design-review-powered-by-mixed-reality',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/dev-test-image-factory',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/cloud-scale-analytics-with-discovery-hub',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/disaster-recovery-enterprise-scale-dr',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/big-compute-with-azure-batch',
        'https://docs.microsoft.com/en-us/azure/architecture/example-scenario/data/hybrid-etl-with-adf',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/loan-credit-risk-analyzer-and-default-modeling',
        'https://docs.microsoft.com/en-us/azure/architecture/reference-architectures/data/cluedin',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/modern-data-warehouse',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/personalized-marketing',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/predicting-length-of-stay-in-hospitals',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/aircraft-engine-monitoring-for-predictive-maintenance-in-aerospace',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/predictive-insights-with-vehicle-telematics',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/quality-assurance',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/real-time-analytics',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/retail-and-e-commerce-using-cosmos-db',
        'https://docs.microsoft.com/en-us/azure/architecture/example-scenario/signalr/',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/disaster-recovery-smb-azure-site-recovery',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/disaster-recovery-smb-double-take-dr',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/speech-services',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/tiered-data-for-analytics',
        'https://docs.microsoft.com/en-us/azure/architecture/solution-ideas/articles/unlock-legacy-data'
    ]
    return sources[id]

def get_leaves(component):
    url = "http://localhost/api/component/" + str(component['id']) + '/leafs'
    resp = requests.get(url=url)

    data = resp.json()

    return data

def summary(file_name):

    with open(file_name) as jsonFile:
        project = json.load(jsonFile)

        model = project['model']

        components = model['components']

        search_space_size = 1
        print("\\begin{tabular}{lc}")
        print("Component Name & Number of matching services \\\\")
        print("\\hline")
        for component in components:

            leaves = get_leaves(component)

            print(component['name'],'&',len(leaves),'\\\\')

            search_space_size *= len(leaves)
        print('\\end{tabular}')


if __name__ == '__main__':

    for i in range(0,31):
        print('\n\\item['+get_title(i)+'] \leavevmode')
        print('\n\\textbf{Source:}\\\\')
        print('\\url{'+get_sources(i)+'}')
        print('\n')
        print('\\textbf{Description:}')
        print('\n')
        print('\\textbf{Components:}')
        print('\n')
        summary("./TestCases/{}.json".format(i+1))

