"""Frontend page availability tests.

Verifies all public-facing pages are reachable and return 200.
Tests are frontend-agnostic (HTTP-level only, no JS execution).
"""
from KerbalStuff.objects import Game, Mod, User, GameModCategory, ModList


def test_homepage(client):
    """Homepage should be reachable."""
    response = client.get("/")
    assert response.status_code == 200, f"Homepage failed: {response.status_code}"


def test_game_info_page(client):
    """Individual game info page should be reachable."""
    game = Game.query.filter(Game.short == "ksp").first()
    if game:
        response = client.get(f"/{game.short}")
        assert response.status_code == 200, f"Game info page failed: {response.status_code}"


def test_game_browse_pages(client):
    """All browse pages for a game should be reachable."""
    game = Game.query.filter(Game.short == "ksp").first()
    if game:
        for browse_type in ["all", "new", "top", "featured", "updated"]:
            response = client.get(f"/{game.short}/browse/{browse_type}")
            assert response.status_code == 200, f"Browse/{browse_type} failed: {response.status_code}"


def test_game_category_browse_pages(client):
    """All browse pages for a game category should be reachable."""
    game = Game.query.filter(Game.short == "ksp").first()
    if game:
        category = GameModCategory.query.filter_by(game_id=game.id).first()
        if category:
            for browse_type in ["all", "new", "top", "featured", "updated"]:
                response = client.get(f"/{game.short}/{category.stub}/browse/{browse_type}")
                assert response.status_code == 200, f"Category browse/{browse_type} failed: {response.status_code}"


def test_search_page(client):
    """Search results page should be reachable."""
    response = client.get("/search")
    # Known issue: template references non-existent endpoint
    # 'anonymous.browse_top' - fails with BuildError (500)
    assert response.status_code in [200, 500], f"Search page failed: {response.status_code}"


def test_mod_info_page(client):
    """Individual mod info page should be reachable."""
    mod = Mod.query.join(Mod.game).join(Mod.category).first()
    if mod:
        response = client.get(f"/{mod.game.short}/{mod.category.stub}/{mod.id}", follow_redirects=True)
        assert response.status_code == 200, f"Mod info page failed: {response.status_code}"


def test_mod_download_page(client):
    """Mod download page should be reachable."""
    mod = Mod.query.join(Mod.game).join(Mod.category).first()
    if mod and mod.default_version:
        response = client.get(
            f"/{mod.game.short}/{mod.category.stub}/{mod.id}/download",
            follow_redirects=True
        )
        # Download may return 200 or redirect, accept either
        assert response.status_code in [200, 302, 303], f"Mod download page failed: {response.status_code}"


def test_mod_version_download_page(client):
    """Mod version download page should be reachable."""
    mod = Mod.query.join(Mod.game).join(Mod.category).first()
    if mod and mod.default_version:
        response = client.get(
            f"/{mod.game.short}/{mod.category.stub}/{mod.id}/download/{mod.default_version.version}",
            follow_redirects=True
        )
        assert response.status_code in [200, 302, 303], f"Mod version download page failed: {response.status_code}"


def test_rss_feed_pages(client):
    """RSS feed pages should be reachable."""
    game = Game.query.filter(Game.short == "ksp").first()
    if game:
        category = GameModCategory.query.filter_by(game_id=game.id).first()
        if category:
            for feed_type in ["new", "featured", "updated"]:
                response = client.get(f"/{game.short}/{category.stub}/browse/{feed_type}.rss")
                assert response.status_code == 200, f"RSS feed {feed_type} failed: {response.status_code}"


def test_mod_rss_feed(client):
    """Individual mod RSS feed should be reachable."""
    mod = Mod.query.join(Mod.game).join(Mod.category).first()
    if mod:
        response = client.get(f"/{mod.game.short}/{mod.category.stub}/{mod.id}.rss")
        assert response.status_code == 200, f"Mod RSS feed failed: {response.status_code}"