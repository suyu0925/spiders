import { SourceEnum, Subject, SubjectDoc } from '@global/interfaces/subject.interface'
import { Injectable, Logger } from '@nestjs/common'
import { InjectModel } from '@nestjs/mongoose'
import * as Crawler from 'crawler'
import * as moment from 'moment'
import { Model } from 'mongoose'

@Injectable()
export class AppService {
  constructor(
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

  async updateSubjectMagnet(title: string, magnet: string) {
    await this.subjectModel.updateOne({ title }, { $set: { magnet } })
  }

  getMaxPageNumber($: any) {
    const lis = $('.page-navigator>li')
    const length = lis.get().length
    let $lastList = $(lis.get(length - 1))
    this.logger.log(`lastList ${$lastList.toString()}`)
    this.logger.log(`$lastList.children('a').text() ${$lastList.children('a').text()}`)
    if ($lastList.children('a').text() === '下一页') {
      $lastList = $lastList.prev()
    }
    return parseInt($lastList.children('a').text(), 10)
  }

  async crawlPage(page: number = 1) {
    return new Promise((resolve, reject) => {
      const c = new Crawler({
        maxConnections: 10,
        // This will be called for each crawled page
        callback: (error: Error, res: any, done2: () => void) => {
          const done = () => {
            this.logger.log(`crawl page ${page} done`)
            done2()
          }

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
                magnet: null,
              }
              // this.logger.log(`${JSON.stringify(subject)}`)
              pageDate = subject.updateTime
              subjects.push(subject)
            }

            // if (moment(latestUpdateDate).isBefore(pageDate)) {
            //   this.logger.log(`next page`)
            //   c.queue('https://www.sshs.xyz/tag/%E9%87%8C%E7%95%AA/2/')
            // }

            const maxPage = this.getMaxPageNumber($)
            this.logger.log(`maxPage: ${maxPage}`)
            if (page === maxPage) {
              done()
              return
            }

            this.saveSubjects(subjects).then((isOverlap) => {
              this.logger.log(`isOverlap ${isOverlap}`)
              // isOverlap = true
              if (!isOverlap) {
                this.crawlPage(page + 1).then(() => {
                  done()
                })
              } else {
                done()
              }
            })
          }
        }
      })

      // const html = fs.readFileSync(`${__dirname}/../sshs.html`)
      // c.queue({ html })
      // c.queue(`https://www.sshs.xyz/tag/%E9%87%8C%E7%95%AA/${page === 1 ? '' : page}`)
      c.queue(`https://www.sshs.xyz/category/anime.html/${page}/`)

      c.on('drain', () => {
        // all task done
        this.logger.log('all done')
        resolve()
      })
    })
  }

  async crawlProducts() {
    const subjects = await this.subjectModel.find({ magnet: null })
    this.logger.log(`there are ${subjects.length} subjects waitting to crawl`)

    return new Promise((resolve, reject) => {
      if (subjects.length === 0) {
        this.logger.log('no new, done')
        resolve()
        return
      }

      const c = new Crawler({
        // rateLimit: 1000, // `maxConnections` will be forced to 1 and between two tasks, minimum time gap is 1000 (ms)
        maxConnections: 10,
        callback: (error: Error, res: any, done2: () => void) => {
          const done = () => {
            this.logger.log(`crawl subject ${res.options.title} done`)
            done2()
          }

          const $ = res.$

          const items = $('.dl-item')
          let magnet = 'no'
          for (let i = 0; i < items.get().length; i++) {
            const $item = $(items.get(i))
            // this.logger.log(`$item.toString() ${$item.toString()}`)
            // this.logger.log(`$item.text() ${$item.text()}`)
            // this.logger.log(`$item.children('a').attr('href') ${$item.children('a').attr('href')}`)
            if ($item.text().trim() === '磁力') {
              magnet = $item.children('a').attr('href')
            }
          }
          // this.logger.log(`magnet ${magnet}`)

          this.updateSubjectMagnet(res.options.title, magnet).then(() => {
            done()
          })
        },
      })

      for (const subject of subjects) {
        this.logger.log(`queue title ${subject.title}, uri: ${subject.href}`)
        c.queue({ uri: subject.href, title: subject.title })
      }
      // const html = fs.readFileSync(`${__dirname}/../sshs_detail.html`)
      // c.queue({ html, title: '123' })

      c.on('drain', () => {
        // all task done
        this.logger.log('all products done')
        resolve()
      })
    })
  }

  async crawl() {
    await this.crawlPage()

    await this.crawlProducts()
  }

  async getMagnet(start: string) {
    const subjects = this.subjectModel.find({
      ...start ? { updateTime: { $gt: moment(start).toDate() } } : {},
      magnet: { $ne: null }
    }, { magnet: 1, updateTime: 1, title: 1 }).sort({ updateTime: 1 }).limit(50)
    return subjects
  }
}
