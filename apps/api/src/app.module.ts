import { Module } from '@nestjs/common';
import { PingController } from './app.controller';

@Module({
  imports: [],
  controllers: [PingController],
  providers: [],
})
export class AppModule {}
