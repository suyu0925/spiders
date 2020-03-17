import { Controller, Get, Query } from '@nestjs/common'
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

  @Get('/magnet')
  async getMagnet(@Query() query: { start: string }) {
    const subjects = await this.appService.getMagnet(query.start)
    return subjects.map(s => s.magnet).join('<br>')
  }
}
