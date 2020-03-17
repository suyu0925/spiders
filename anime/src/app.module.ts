import { SubjectSchema } from '@global/schemas/subject.schema'
import { Module } from '@nestjs/common'
import { ConfigModule } from '@nestjs/config'
import { MongooseModule } from '@nestjs/mongoose'
import { AppController } from './app.controller'
import { AppService } from './app.service'
import configuration from './config/configuration'

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      load: [configuration],
    }),
    MongooseModule.forRoot('mongodb://localhost/anime'),
    MongooseModule.forFeature([{ name: 'subject', schema: SubjectSchema, collection: 'subjects' }]),
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {
}
