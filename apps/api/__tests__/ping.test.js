const request = require('supertest');
const app = require('../index');

describe('GET /v1/ping', () => {
  it('should return pong', async () => {
    const res = await request(app).get('/v1/ping');
    expect(res.statusCode).toEqual(200);
    expect(res.body).toHaveProperty('message', 'pong');
  });
});