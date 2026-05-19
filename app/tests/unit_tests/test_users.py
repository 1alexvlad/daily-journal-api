import pytest 

from httpx import AsyncClient

@pytest.mark.asyncio
class TestUser:

    async def test_register_success(self, ac: AsyncClient):
        response = await ac.post('/auth/register', json={
            'email' : 'newuser@mail.com', 
            'hashed_password': 'new_user_password', 
            'full_name': "TEST User 2", 
        })

        assert response.status_code == 200
        data = response.json()
        assert data['email'] == 'newuser@mail.com'
        assert 'id' in data
        
    async def test_logout_user_success(self, authenticated_ac: AsyncClient):
        assert 'session_id' in authenticated_ac.cookies, "session_id должен существовать до выхода из системы"

        response = await authenticated_ac.post('/auth/logout')
        assert response.status_code == 200
        assert 'session_id' not in authenticated_ac.cookies, "'session_id' не был удален после выхода"

    async def test_register_duplicate_email(self, ac: AsyncClient):
        response_first = await ac.post('/auth/register', json={
            'email': 'newuser@mail.com',
            'hashed_password': 'new_user_password',
            'full_name': "TEST User",
        })
        assert response_first.status_code == 200, "First registration should succeed"
        
        response_second = await ac.post('/auth/register', json={
            'email': 'newuser@mail.com',
            'hashed_password': 'new_user_duplicated',
            'full_name': "TEST User duplicated",
        })
        assert response_second.status_code == 409

    async def test_register_invalid_email(self, ac: AsyncClient):
        response = await ac.post('/auth/register', json={
            'email': 'mail', 
            'hashed_password': 'wrong_email', 
            'full_name': "TEST", 
        })
        assert response.status_code == 422


    async def test_login_user_success(self, ac: AsyncClient, test_user ):
        response_login = await ac.post('/auth/login', json={
            'email':"user@example.com",
            'hashed_password': 'user_password',
        })
        assert response_login.status_code == 200
        assert 'session_id' in ac.cookies

    
        async def test_user_by_id(self, ac: AsyncClient, test_staff, test_user):
            response_login = await ac.post('/auth/login', json={
                'email': "staff@example.com",
                'hashed_password': 'staff_password',
            })
            assert response_login.status_code == 200
            
            user_id = test_user.id
            
            response = await ac.get(f'/auth/id/{user_id}')
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            
            assert data['email'] == test_user.email
            assert data['id'] == test_user.id
            assert data['full_name'] == test_user.full_name
        
    async def test_user_by_id_not_found(self, ac: AsyncClient, test_admin):
        
        login_response = await ac.post('/auth/login', json={
            'email': "admin@example.com",
            'hashed_password': 'admin_password',
        })
        assert login_response.status_code == 200
        
        response = await ac.get('/auth/id/1000')
        assert response.status_code == 404

    async def test_delete_user(self, ac: AsyncClient, test_admin):
        
        login_response = await ac.post('/auth/login', json={
            'email': "admin@example.com",
            'hashed_password': 'admin_password',
        })
        assert login_response.status_code == 200
        
        response = await ac.delete('/auth')
        assert response.status_code == 200


class TestUpdateUser:
        
    @pytest.mark.parametrize("update_data, expected_field", [
        ({"full_name": "new name"}, "full_name"),
        ({"email": "newemail@example.com"}, "email"),
        ({"email": "newemail2@example.com", "full_name": "sdfk"}, "full_name"),
    ])
    @pytest.mark.asyncio
    async def test_update_user_success(
        self, ac: AsyncClient, test_admin, test_user, update_data, expected_field
    ):
        await ac.post('/auth/login', json={
            'email': test_admin.email,
            'hashed_password': 'admin_password',
        })
        
        response = await ac.patch('/auth/update', params={'user_id': test_user.id}, json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data[expected_field] == update_data[expected_field]
    
    @pytest.mark.parametrize("email, expected_status", [
        ("invalid-email", 422),
        ("sdfs@ftld", 422),
        ("", 422),
        ("valid@example.com", 200),
    ])
    @pytest.mark.asyncio
    async def test_update_user_email_validation(
        self, ac: AsyncClient, test_admin, test_user, email, expected_status
    ):
        await ac.post('/auth/login', json={
            'email': test_admin.email,
            'hashed_password': 'admin_password',
        })
        
        response = await ac.patch('/auth/update', params={'user_id': test_user.id}, json={
            'email': email
        })
        
        assert response.status_code == expected_status