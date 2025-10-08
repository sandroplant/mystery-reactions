import * as request from 'supertest';
import { Test } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import { AppModule } from './app.module';

describe('AppController (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  it('/GET healthz', () => {
    return request(app.getHttpServer())
      .get('/healthz')
      .expect(200)
      .expect({ ok: true });
  });

  afterAll(async () => {
    await app.close();
  });
});
