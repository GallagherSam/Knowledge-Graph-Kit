from app.models import ProjectProperties


def test_create_project_integration(tools_instance):
    """
    Integration test for the create_project tool.
    Verifies that a project is created in the database with the correct properties.
    """
    # 1. Arrange
    name = "Project Gemini"
    description = "A project to build a next-generation AI assistant."
    status = "active"
    tags = ["ai", "development", "llm"]

    # 2. Act
    created_project = tools_instance.projects.create_project(
        name=name, description=description, status=status, tags=tags
    )

    # 3. Assert
    assert created_project is not None
    assert "id" in created_project
    assert created_project["type"] == "Project"
    
    properties = created_project["properties"]
    assert properties["name"] == name
    assert properties["description"] == description
    assert properties["status"] == status
    assert properties["tags"] == tags

    # 4. Verify directly in the database
    with tools_instance.get_db() as db:
        from app.database import NodeModel
        db_node = db.query(NodeModel).filter(NodeModel.id == created_project["id"]).first()
        
        assert db_node is not None
        assert db_node.type == "Project"
        
        db_properties = db_node.properties
        assert db_properties["name"] == name
        assert db_properties["description"] == description
        assert db_properties["status"] == status
        assert db_properties["tags"] == tags
        
        # Verify Pydantic model validation
        validated_props = ProjectProperties(**db_properties)
        assert validated_props.name == name

def test_update_project_integration(tools_instance):
    """
    Integration test for the update_project tool.
    Verifies that a project's properties are correctly updated in the database,
    and that unchanged properties are preserved.
    """
    # 1. Arrange: Create an initial project to be updated.
    initial_name = "Project Alpha"
    initial_description = "Initial phase of the project."
    initial_tags = ["prototype", "research"]
    created_project = tools_instance.projects.create_project(
        name=initial_name, description=initial_description, tags=initial_tags, status="active"
    )
    project_id = created_project["id"]

    # Define the updates
    new_description = "The project has been updated to the beta phase."
    new_status = "archived"

    # 2. Act: Update the project with new properties.
    updated_project = tools_instance.projects.update_project(
        project_id=project_id, description=new_description, status=new_status
    )

    # 3. Assert: Check the dictionary returned by the tool.
    assert updated_project is not None
    assert updated_project["id"] == project_id
    
    updated_properties = updated_project["properties"]
    assert updated_properties["name"] == initial_name  # Should remain unchanged
    assert updated_properties["description"] == new_description
    assert updated_properties["status"] == new_status
    assert updated_properties["tags"] == initial_tags  # Should remain unchanged

    # 4. Verify: Check the state directly in the database.
    with tools_instance.get_db() as db:
        from app.database import NodeModel
        db_node = db.query(NodeModel).filter(NodeModel.id == project_id).first()
        
        assert db_node is not None
        db_properties = db_node.properties
        
        assert db_properties["name"] == initial_name
        assert db_properties["description"] == new_description
        assert db_properties["status"] == new_status
        assert db_properties["tags"] == initial_tags

def test_project_search_integration(tools_instance):
    """
    Integration test for the search_nodes tool, focusing on projects.
    Verifies that the search correctly finds projects by name, description, and tags.
    """
    # 1. Arrange: Create a set of diverse projects to search through.
    project1 = tools_instance.projects.create_project(
        name="Data Migration Initiative",
        description="Moving legacy data to a new cloud platform.",
        tags=["data", "cloud"]
    )
    project2 = tools_instance.projects.create_project(
        name="Frontend Redesign",
        description="A complete overhaul of the user interface.",
        tags=["ui", "design", "frontend"]
    )

    # 2. Act & Assert: Perform various search queries.

    # Test searching by a unique name keyword
    results_migration = tools_instance.shared.search_nodes(query="Migration", node_type="Project")
    assert len(results_migration) == 1
    assert results_migration[0]["id"] == project1["id"]

    # Test searching by a unique description keyword
    results_interface = tools_instance.shared.search_nodes(query="interface", node_type="Project")
    assert len(results_interface) == 1
    assert results_interface[0]["id"] == project2["id"]

    # Test searching by a shared tag
    results_data = tools_instance.shared.search_nodes(node_type="Project", tags=["data"])
    assert len(results_data) == 1
    assert results_data[0]["id"] == project1["id"]

    # Test searching with a query that matches nothing
    results_nothing = tools_instance.shared.search_nodes(query="nonexistent", node_type="Project")
    assert len(results_nothing) == 0
