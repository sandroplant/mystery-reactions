import { Controller, Get } from '@nestjs/common';

@Controller('v1')
export class PingController {
  @Get('ping')
  getPing() {
    return { ok: true };
  }
}
