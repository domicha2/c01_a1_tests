import pytest
import requests
import json


class MovieInterface():

    def __init__(self):
        self.session = requests.Session()
        self.base_url = "http://localhost:8080/api/v1/"

    def send_request(self, request_type, data, resource):
        req = requests.Request(
            request_type,
            self.base_url + resource,
            data=json.dumps(data),
        )
        prep = self.session.prepare_request(req)
        return self.session.send(prep)

    def add_actor(self, name, actorId, data=None):
        if data == None:
            data = {"name": name, "actorId": actorId}
        return self.send_request("PUT", data, "addActor")

    def add_movie(self, name, movieId, data=None):
        if data == None:
            data = {"name": name, "movieId": movieId}
        return self.send_request("PUT", data, "addMovie")

    def add_relationship(self, actorId, movieId, data=None):
        if data == None:
            data = {"actorId": actorId, "movieId": movieId}
        return self.send_request("PUT", data, "addRelationship")

    def get_actor(self, actorId, data=None):
        if data == None:
            data = {"actorId": actorId}
        return self.send_request("GET", data, "getActor")

    def get_movie(self, movieId, data=None):
        if data == None:
            data = {"movieId": movieId}
        return self.send_request("GET", data, "getMovie")

    def has_relationship(self, actorId, movieId, data=None):
        if data == None:
            data = {"actorId": actorId, "movieId": movieId}
        return self.send_request("GET", data, "hasRelationship")

    def compute_bacon_number(self, actorId, data=None):
        if data == None:
            data = {"actorId": actorId}
        return self.send_request("GET", data, "computeBaconNumber")

    def compute_bacon_path(self, actorId, data=None):
        if data == None:
            data = {"actorId": actorId}
        return self.send_request("GET", data, "computeBaconPath")

    def reset(self):
        return self.session.get(self.base_url + "reset")


@pytest.fixture
def movie_interface():
    return MovieInterface()


def test_reset(movie_interface):
    response = movie_interface.reset()
    assert response.status_code == 200


def test_getActor_dne(movie_interface):
    response = movie_interface.get_actor("1")
    assert response.status_code == 404


def test_getMovie_dne(movie_interface):
    response = movie_interface.get_movie("1")
    assert response.status_code == 404


def test_add_actor(movie_interface):
    response = movie_interface.add_actor("kevin bacon", "1")
    assert response.status_code == 200

    response = movie_interface.add_actor("kevin baecon", "1")  # you can't add the same id again
    assert response.status_code == 400

    response = movie_interface.add_actor("kevin bacon", "1")
    # same name and id is not cool
    assert response.status_code == 400

def test_add_movie(movie_interface):
    response = movie_interface.add_movie("space jam", "1")
    assert response.status_code == 200

    response = movie_interface.add_movie("kevin baecon", "1")  # you can't add the same id again
    assert response.status_code == 400

    response = movie_interface.add_actor("space jam", "1")
    # same name and id is not cool
    assert response.status_code == 400

def test_add_relationship(movie_interface):
    response = movie_interface.add_relationship("1", "1")
    assert response.status_code == 200
    
    response = movie_interface.add_relationship("2", "1")
    # actor doesnt exist
    assert response.status_code == 404

    response = movie_interface.add_relationship("1", "2")
    # movie doesnt exist
    assert response.status_code == 404

    response = movie_interface.add_relationship("2", "2")
    # movie doesnt exist
    assert response.status_code == 404

    response = movie_interface.add_relationship("1", "1")
    # relationship already exists
    assert response.status_code == 400


def test_getActor(movie_interface):
    # actor in a movie
    response = movie_interface.get_actor("1")
    assert response.status_code == 200
    assert response.json() == {"name": "kevin bacon", "actorId": "1", "movies": ["1"]}

    # actor not in a movie
    response = movie_interface.add_actor("poops", "3")
    assert response.status_code == 200

    response = movie_interface.get_actor("3")
    assert response.status_code == 200
    assert response.json() == {"name": "poops", "actorId": "3", "movies": []}


def test_getMovie(movie_interface):
    response = movie_interface.get_movie("1")
    assert response.status_code == 200
    assert response.json() == {"name": "space jam", "movieId": "1", "actors": ["1"]}

    # actor not in a movie
    response = movie_interface.add_movie("naruto", "3")
    assert response.status_code == 200

    response = movie_interface.get_actor("3")
    assert response.status_code == 200
    assert response.json() == {"name": "naruto", "movieId": "3", "actors": []}


def test_has_relationship(movie_interface):
    response = movie_interface.add_relationship("1", "1")
    assert response.status_code == 200
    assert response.json() == {"actorId": "1",  "movieId": "1", "hasRelationship": True}

    response = movie_interface.add_relationship("2", "1")
    # actor doesnt exist
    assert response.status_code == 404

    response = movie_interface.add_relationship("1", "2")
    # movie doesnt exist
    assert response.status_code == 404

    response = movie_interface.add_relationship("2", "2")
    # movie doesnt exist
    assert response.status_code == 404

    response = movie_interface.add_relationship("3", "1")
    # no relationship already exists
    assert response.status_code == 200
    assert response.json() == {"actorId": "3", "movieId": "1", "hasRelationship": False}

    response = movie_interface.add_relationship("1", "3")
    # no relationship already exists one more
    assert response.status_code == 200
    assert response.json() == {"actorId": "1", "movieId": "3", "hasRelationship": False}

def test_garbage_input(movie_interface):
    response = movie_interface.add_actor("trash", "trash", {"trash": "trash"})
    assert response.status_code == 400

    response = movie_interface.add_movie("trash", "trash", {"trash": "trash"})
    assert response.status_code == 400

    response = movie_interface.add_relationship("trash", "trash", {"trash": "trash"})
    assert response.status_code == 400

    response = movie_interface.get_actor("trash", "trash", {"trash": "trash"})
    assert response.status_code == 400

    response = movie_interface.get_movie("trash", "trash", {"trash": "trash"})
    assert response.status_code == 400

    response = movie_interface.has_relationship("trash", "trash", {"trash": "trash"})
    assert response.status_code == 400
