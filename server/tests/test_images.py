from cp.images import set_photo_coverage_href


def test_set_photo_coverage_href():
    coverage = {
        "coverage_id": "b808c78c-6859-41df-aabd-bd54b3fb4db9",
        "workflow_status": "completed",
        "coverage_status": "coverage intended",
        "watches": [],
        "assigned_user_name": "john doe",
        "scheduled": "2024-06-16T14:00:00+0000",
        "delivery_id": None,
        "coverage_provider": "Stringer",
        "planning_id": "f71ed214-9fa7-4de4-834b-9da85276015f",
        "deliveries": [
            {
                "publish_time": "2024-06-14T12:49:38+0000",
                "delivery_state": "published",
                "delivery_href": "example.com",
                "sequence_no": 0,
            }
        ],
        "slugline": "picture slug",
        "assigned_desk_name": "Test",
        "assigned_desk_email": "foo@bar.com",
        "assigned_user_email": "petr@localhost",
        "publish_time": "2024-06-14T12:49:38+0000",
        "genre": [],
        "coverage_type": "picture",
    }
    href = set_photo_coverage_href(coverage, {}, [])
    assert "https://www.cpimages.com/CS.aspx?VP3=DirectSearch&FT=picture%20slug" == href
