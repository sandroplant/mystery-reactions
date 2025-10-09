import { Module, Controller, Get } from '@nestjs/common';

@Controller()
class AppController {
  @Get('healthz')
  getHealth() {
    return { ok: true };
  }
}

@Module({
  controllers: [AppController],
})
export class AppModule {}
