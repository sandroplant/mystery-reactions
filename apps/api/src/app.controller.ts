import { Controller, Get } from '@nestjs/common';

@Controller()
export class AppController {
  @Get('healthz')
  getHealth(): { ok: boolean } {
    return { ok: true };
  }
}
