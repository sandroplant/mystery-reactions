import { Test, TestingModule } from '@nestjs/testing';
import { PingController } from '../src/app.controller';

describe('PingController', () => {
  let pingController: PingController;

  beforeEach(async () => {
    const app: TestingModule = await Test.createTestingModule({
      controllers: [PingController],
    }).compile();

    pingController = app.get<PingController>(PingController);
  });

  describe('getPing', () => {
    it('should return { ok: true }', () => {
      expect(pingController.getPing()).toEqual({ ok: true });
    });
  });
});
