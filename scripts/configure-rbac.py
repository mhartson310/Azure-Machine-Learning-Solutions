from azure.identity import DefaultAzureCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.machinelearningservices import MachineLearningServicesMgmtClient

def configure_aml_security(subscription_id, resource_group, workspace_name):
    credential = DefaultAzureCredential()
    ml_client = MachineLearningServicesMgmtClient(credential, subscription_id)
    auth_client = AuthorizationManagementClient(credential, subscription_id)
    
    # Get workspace ID
    workspace = ml_client.workspaces.get(resource_group, workspace_name)
    
    # Security groups
    roles = {
        "ML Security Admins": "Contributor",
        "ML Data Scientists": "AzureML Data Scientist",
        "ML Auditors": "Reader"
    }
    
    # Assign RBAC roles
    for group_name, role_name in roles.items():
        role_definition = next(
            r for r in auth_client.role_definitions.list(workspace.id) 
            if r.role_name == role_name
        )
        
        auth_client.role_assignments.create(
            workspace.id,
            "guid",  # Generate new GUID
            {
                "properties": {
                    "roleDefinitionId": role_definition.id,
                    "principalId": f"/subscriptions/{subscription_id}/providers/Microsoft.Aadiam/groups/{group_name}",
                    "principalType": "Group"
                }
            }
        )
    
    print(f"Configured RBAC for {workspace_name} workspace")

if __name__ == "__main__":
    configure_aml_security(
        subscription_id="your-sub-id",
        resource_group="aml-sec-rg",
        workspace_name="secure-ml-prod"
    )
