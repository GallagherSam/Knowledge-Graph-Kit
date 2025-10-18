from app.models import NoteProperties


def test_create_note_integration(tools_instance):
    """
    Integration test for the create_note tool.
    Verifies that a note is created in the database with the correct properties.
    """
    # 1. Arrange
    title = "Test Note"
    content = "This is a test note."
    tags = ["test", "integration"]

    # 2. Act
    created_note = tools_instance.notes.create_note(title=title, content=content, tags=tags)

    # 3. Assert
    assert created_note is not None
    assert "id" in created_note
    assert created_note["type"] == "Note"

    properties = created_note["properties"]
    assert properties["title"] == title
    assert properties["content"] == content
    assert properties["tags"] == tags

    # 4. Verify directly in the database
    with tools_instance.get_db() as db:
        from app.database import NodeModel

        db_node = db.query(NodeModel).filter(NodeModel.id == created_note["id"]).first()

        assert db_node is not None
        assert db_node.type == "Note"

        db_properties = db_node.properties
        assert db_properties["title"] == title
        assert db_properties["content"] == content
        assert db_properties["tags"] == tags

        # Verify Pydantic model validation
        validated_props = NoteProperties(**db_properties)
        assert validated_props.title == title


def test_update_note_integration(tools_instance):
    """
    Integration test for the update_note tool.
    Verifies that a note's properties are correctly updated in the database,
    and that unchanged properties are preserved.
    """
    # 1. Arrange: Create an initial note to be updated.
    initial_title = "Initial Title"
    initial_content = "Initial content."
    initial_tags = ["tag1", "tag2"]
    created_note = tools_instance.notes.create_note(
        title=initial_title, content=initial_content, tags=initial_tags
    )
    note_id = created_note["id"]
    original_modified_at = created_note["properties"]["modified_at"]

    # Define the updates
    new_title = "Updated Title"
    new_tags = ["tag1", "updated"]

    # 2. Act: Update the note with new properties.
    updated_note = tools_instance.notes.update_note(note_id=note_id, title=new_title, tags=new_tags)

    # 3. Assert: Check the dictionary returned by the tool.
    assert updated_note is not None
    assert updated_note["id"] == note_id

    updated_properties = updated_note["properties"]
    assert updated_properties["title"] == new_title
    assert updated_properties["content"] == initial_content  # Should remain unchanged
    assert updated_properties["tags"] == new_tags
    assert updated_properties["modified_at"] > original_modified_at

    # 4. Verify: Check the state directly in the database.
    with tools_instance.get_db() as db:
        from app.database import NodeModel

        db_node = db.query(NodeModel).filter(NodeModel.id == note_id).first()

        assert db_node is not None
        db_properties = db_node.properties

        assert db_properties["title"] == new_title
        assert db_properties["content"] == initial_content  # Verify unchanged property
        assert db_properties["tags"] == new_tags
        assert db_properties["modified_at"] == updated_properties["modified_at"]


def test_node_search_integration(tools_instance):
    """
    Integration test for the search_nodes tool, focusing on notes.
    Verifies that the search correctly finds notes by title, content, and tags.
    """
    # 1. Arrange: Create a set of diverse notes to search through.
    note1 = tools_instance.notes.create_note(
        title="Unique Apple Note", content="Content about oranges.", tags=["fruit", "food"]
    )
    note2 = tools_instance.notes.create_note(
        title="Another Note", content="This one is about a unique banana.", tags=["fruit", "yellow"]
    )
    tools_instance.notes.create_note(
        title="Third Note", content="Just some random text.", tags=["random"]
    )

    # 2. Act & Assert: Perform various search queries.

    # Test searching by a unique title keyword
    results_apple = tools_instance.shared.search_nodes(query="Apple", node_type="Note")
    assert len(results_apple) == 1
    assert results_apple[0]["id"] == note1["id"]

    # Test searching by a unique content keyword
    results_banana = tools_instance.shared.search_nodes(query="banana", node_type="Note")
    assert len(results_banana) == 1
    assert results_banana[0]["id"] == note2["id"]

    # Test searching by a shared tag
    results_fruit = tools_instance.shared.search_nodes(node_type="Note", tags=["fruit"])
    assert len(results_fruit) == 2
    assert {res["id"] for res in results_fruit} == {note1["id"], note2["id"]}

    # Test searching with a query that matches nothing
    results_nothing = tools_instance.shared.search_nodes(query="nonexistent", node_type="Note")
    assert len(results_nothing) == 0

    # Test searching with both a query and a tag
    results_orange_fruit = tools_instance.shared.search_nodes(
        query="oranges", node_type="Note", tags=["fruit"]
    )
    assert len(results_orange_fruit) == 1
    assert results_orange_fruit[0]["id"] == note1["id"]

    # Test searching with a query and a non-matching tag
    results_apple_random = tools_instance.shared.search_nodes(
        query="Apple", node_type="Note", tags=["random"]
    )
    assert len(results_apple_random) == 0


def test_node_semantic_search_integration(tools_instance):
    """
    Integration test for the semantic_search tool.
    Verifies that the search returns conceptually related notes based on
    semantic similarity, not just keyword matching.
    """
    # 1. Arrange: Create nodes with distinct semantic concepts.
    note_fruit_1 = tools_instance.notes.create_note(
        title="Fruit Basket", content="Apples, bananas, and oranges are great for a balanced diet."
    )
    note_fruit_2 = tools_instance.notes.create_note(
        title="Tropical Tastes", content="Mangoes and pineapples are delicious tropical fruits."
    )
    note_tech = tools_instance.notes.create_note(
        title="Software Development", content="Building applications with Python and JavaScript."
    )
    # Also create a non-Note node to ensure it's filtered out
    task_unrelated = tools_instance.tasks.create_task(description="File the TPS reports.")

    # 2. Act: Perform a semantic search for a concept, not a keyword.
    # The query "healthy snacks" is semantically related to fruit.
    search_results = tools_instance.shared.semantic_search(
        query="healthy snacks",
        node_type="Note",  # Filter to only include notes
    )

    # 3. Assert: Verify the results are ordered by semantic relevance.
    assert len(search_results) >= 2  # Should find at least the two fruit notes

    result_ids = [res["id"] for res in search_results]

    # The top result should be one of the fruit notes.
    assert result_ids[0] in [note_fruit_1["id"], note_fruit_2["id"]]

    # The technology note should be ranked lower than the fruit notes.
    try:
        tech_note_index = result_ids.index(note_tech["id"])
        fruit_note_1_index = result_ids.index(note_fruit_1["id"])

        assert fruit_note_1_index < tech_note_index
    except ValueError:
        # If the tech note is not in the results at all, the test passes.
        pass

    # Ensure the unrelated task was not returned.
    assert task_unrelated["id"] not in result_ids
