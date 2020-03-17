import { Controller, Get } from '@nestjs/common'
import { AppService } from './app.service'

@Controller('/')
export class AppController {
  constructor(
    private readonly appService: AppService,
  ) { }

  @Get('/')
  async hello() {
    return 'hello'
  }

  @Get('/crawl')
  async crawl() {
    await this.appService.crawl()
    return 'crawl done'
  }
}
