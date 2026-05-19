import pytest 

from httpx import AsyncClient



@pytest.mark.asyncio
class TestNotes:
    
    async def test_create_and_get_note(self, ac: AsyncClient, test_user):
        login_resp = await ac.post('/auth/login', json={
            'email': test_user.email,
            'hashed_password': 'user_password',
        })
        assert login_resp.status_code == 200
        
        create_resp = await ac.post('/entries/', params={
            'title': 'Test',
            'content': 'Content'
        })
        print(f"Create status: {create_resp.status_code}")
        print(f"Create response: {create_resp.text}")
        assert create_resp.status_code == 200


    async def test_unautheicated_access(self, ac: AsyncClient):
        post_resp = await ac.post('/entries/', params={'title': 'sdfsdf', 'content': 'sdfdsf'})
        assert post_resp.status_code == 401
        
        get_resp = await ac.get('/entries/')
        assert get_resp.status_code == 401

    async def test_update_note_success(self, ac: AsyncClient, test_user):
        await ac.post('/auth/login', json={
            'email': test_user.email,
            'hashed_password': 'user_password',
        })

        create_response = await ac.post('/entries/', params={
            'title': 'Old Title',
            'content': 'Old Content'
        })
        assert create_response.status_code == 200, f"Create failed: {create_response.text}"
        
        data = create_response.json()
        note_id = data.get('id') 
        
        assert note_id is not None, f"No id in response: {data}"
        
        response = await ac.put(f'/entries/{note_id}', params={
            'title': 'New Title',
            'content': 'New Content'
        })
        assert response.status_code == 200
        data = response.json()
        assert data['title'] == 'New Title'
        assert data['content'] == 'New Content'

    async def test_update_note_partial(self, ac: AsyncClient, test_user):
        await ac.post('/auth/login', json={
            'email': test_user.email,
            'hashed_password': 'user_password',
        })
        
        create_resp = await ac.post('/entries/', params={
            'title': 'Original',
            'content': 'Original Content'
        })
        note_id = create_resp.json()['id']
        
        response = await ac.put(f'/entries/{note_id}', params={'title': 'Updated Title'})
        
        assert response.status_code == 200
        data = response.json()
        assert data['title'] == 'Updated Title'
        assert data['content'] == 'Original Content'

    
    async def test_update_note_not_found(self, ac: AsyncClient, test_user):
        await ac.post('/auth/login', json={
            'email': test_user.email,
            'hashed_password': 'user_password',
        })
        
        response = await ac.put('/entries/99999', params={'title': 'New Title'})
        assert response.status_code == 500


    async def test_delete_note_success(self, ac: AsyncClient, test_user):
        await ac.post('/auth/login', json={
            'email': test_user.email,
            'hashed_password': 'user_password',
        })
        
        create_resp = await ac.post('/entries/', params={
            'title': 'To Delete',
            'content': 'Content'
        })

        note_id = create_resp.json()['id']
        user_id_in_note = create_resp.json().get('user_id')
        print(f"Note id: {note_id}, user_id in note: {user_id_in_note}")
    
    async def test_delete_note_not_found(self, ac: AsyncClient, test_user):
        await ac.post('/auth/login', json={
            'email': test_user.email,
            'hashed_password': 'user_password',
        })
        
        response = await ac.delete('/entries/99999')
        assert response.status_code == 500
    