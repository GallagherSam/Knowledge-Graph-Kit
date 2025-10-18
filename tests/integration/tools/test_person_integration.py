from app.models import PersonProperties


def test_create_person_integration(tools_instance):
    """
    Integration test for the create_person tool.
    Verifies that a person is created in the database with the correct properties.
    """
    # 1. Arrange
    name = "John Doe"
    tags = ["contact", "engineering"]
    metadata = {"email": "john.doe@example.com", "role": "Software Engineer"}

    # 2. Act
    created_person = tools_instance.persons.create_person(name=name, tags=tags, metadata=metadata)

    # 3. Assert
    assert created_person is not None
    assert "id" in created_person
    assert created_person["type"] == "Person"
    
    properties = created_person["properties"]
    assert properties["name"] == name
    assert properties["tags"] == tags
    assert properties["metadata"] == metadata

    # 4. Verify directly in the database
    with tools_instance.get_db() as db:
        from app.database import NodeModel
        db_node = db.query(NodeModel).filter(NodeModel.id == created_person["id"]).first()
        
        assert db_node is not None
        assert db_node.type == "Person"
        
        db_properties = db_node.properties
        assert db_properties["name"] == name
        assert db_properties["tags"] == tags
        assert db_properties["metadata"] == metadata
        
        # Verify Pydantic model validation
        validated_props = PersonProperties(**db_properties)
        assert validated_props.name == name

def test_update_person_integration(tools_instance):
    """
    Integration test for the update_person tool.
    Verifies that a person's properties are correctly updated in the database,
    and that unchanged properties are preserved.
    """
    # 1. Arrange: Create an initial person to be updated.
    initial_name = "Jane Doe"
    initial_tags = ["contact", "product"]
    initial_metadata = {"email": "jane.doe@example.com"}
    created_person = tools_instance.persons.create_person(
        name=initial_name, tags=initial_tags, metadata=initial_metadata
    )
    person_id = created_person["id"]

    # Define the updates
    new_name = "Jane Smith"
    new_metadata = {"email": "jane.smith@example.com", "status": "active"}

    # 2. Act: Update the person with new properties.
    updated_person = tools_instance.persons.update_person(
        person_id=person_id, name=new_name, metadata=new_metadata
    )

    # 3. Assert: Check the dictionary returned by the tool.
    assert updated_person is not None
    assert updated_person["id"] == person_id
    
    updated_properties = updated_person["properties"]
    assert updated_properties["name"] == new_name
    assert updated_properties["tags"] == initial_tags  # Should remain unchanged
    assert updated_properties["metadata"] == new_metadata

    # 4. Verify: Check the state directly in the database.
    with tools_instance.get_db() as db:
        from app.database import NodeModel
        db_node = db.query(NodeModel).filter(NodeModel.id == person_id).first()
        
        assert db_node is not None
        db_properties = db_node.properties
        
        assert db_properties["name"] == new_name
        assert db_properties["tags"] == initial_tags # Verify unchanged property
        assert db_properties["metadata"] == new_metadata

def test_person_search_integration(tools_instance):
    """
    Integration test for the search_nodes tool, focusing on persons.
    Verifies that the search correctly finds persons by name and tags.
    """
    # 1. Arrange: Create a set of diverse persons to search through.
    person1 = tools_instance.persons.create_person(
        name="Alice Johnson",
        tags=["developer", "frontend"]
    )
    person2 = tools_instance.persons.create_person(
        name="Bob Williams",
        tags=["developer", "backend"]
    )

    # 2. Act & Assert: Perform various search queries.

    # Test searching by a unique name
    results_alice = tools_instance.shared.search_nodes(query="Alice", node_type="Person")
    assert len(results_alice) == 1
    assert results_alice[0]["id"] == person1["id"]

    # Test searching by a shared tag
    results_developer = tools_instance.shared.search_nodes(node_type="Person", tags=["developer"])
    assert len(results_developer) == 2
    assert {res["id"] for res in results_developer} == {person1["id"], person2["id"]}

    # Test searching with a query that matches nothing
    results_nothing = tools_instance.shared.search_nodes(query="nonexistent", node_type="Person")
    assert len(results_nothing) == 0
