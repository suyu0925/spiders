import { ProductDoc } from '@global/interfaces/product.interface'
import { SourceEnum, Subject, SubjectDoc } from '@global/interfaces/subject.interface'
import { Injectable, Logger } from '@nestjs/common'
import { InjectModel } from '@nestjs/mongoose'
import * as Crawler from 'crawler'
import * as moment from 'moment'
import { Model } from 'mongoose'

@Injectable()
export class AppService {
  constructor(
    @InjectModel('product') private readonly productModel: Model<ProductDoc>,
    @InjectModel('subject') private readonly subjectModel: Model<SubjectDoc>,
  ) { }

  private readonly logger = new Logger(AppService.name)

  async saveSubjects(subjects: Subject[]) {
    let isOverlap = false
    for (const subject of subjects) {
      const sub = await this.subjectModel.findOne({ title: subject.title })
      if (!sub) {
        await this.subjectModel.create(subject)
      } else {
        isOverlap = true
      }
    }
    return isOverlap
  }

  async crawlPage(page?: number) {
    // TODO:
  }

  async crawl() {
    return new Promise((resolve, reject) => {
      const c = new Crawler({
        maxConnections: 10,
        // This will be called for each crawled page
        callback: (error: Error, res: any, done: () => void) => {
          if (error) {
            this.logger.error(error)
            done()
          } else {
            const $ = res.$
            // $ is Cheerio by default
            // a lean implementation of core jQuery designed specifically for the server
            const articles = $('article.excerpt')
            let pageDate: Date
            const subjects: Subject[] = []

            for (let i = 0; i < articles.get().length; i++) {
              const $article = $(articles.get(i))
              // this.logger.log(`${i}:`)
              const subject: Subject = {
                thumbnail: $article.find('img.thumb').attr('data-src'),
                href: $article.children('a').attr('href'),
                title: $article.find('header>h2>a').text(),
                updateTime: moment($article.find('time').text().trim()).toDate(),
                source: SourceEnum.sshs,
              }
              // this.logger.log(`${JSON.stringify(subject)}`)
              pageDate = subject.updateTime
              subjects.push(subject)
            }

            // if (moment(latestUpdateDate).isBefore(pageDate)) {
            //   this.logger.log(`next page`)
            //   c.queue('https://www.sshs.xyz/tag/%E9%87%8C%E7%95%AA/2/')
            // }

            this.saveSubjects(subjects).then((isOverlap) => {
              this.logger.log(`isOverlap ${isOverlap}`)
              if (!isOverlap) {
                done()
              } else {
                done()
              }
            })
          }
        }
      })

      c.queue('https://www.sshs.xyz/tag/%E9%87%8C%E7%95%AA/')

      c.on('drain', () => {
        // all task done
        this.logger.log('all done')
        resolve()
      })
    })
  }
}
