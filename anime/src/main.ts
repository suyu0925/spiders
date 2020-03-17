if (!process.env.IS_TS_NODE) {
  // tslint:disable-next-line:no-var-requires
  require('module-alias/register')
}

import { INestApplication, Logger } from '@nestjs/common'
import { NestFactory } from '@nestjs/core'
import { AppModule } from './app.module'

const logger = new Logger('main')
let app: INestApplication

async function bootstrap() {
  app = await NestFactory.create(AppModule)
  // 在调试模式下，最好不要开这个，会有问题
  // app.enableShutdownHooks()
  app.enableCors()

  await app.listen(app.get('ConfigService').get('port'))

  if (process.send) {
    process.send('ready')
  }
}

bootstrap()

process.on('SIGINT', () => {
  logger.log(`recieve SIGINT`)
  app.close()
    .then(() => {
      logger.log(`now we cat exit gracefully`)
      process.exit(0)
    })
    .catch((err) => {
      logger.error(`shutdown catch ${err.stack}`)
      process.exit(-1)
    })
})
