const Crawler = require('crawler')
const moment = require('moment')
const fs = require('fs')

const logger = console

const c = new Crawler({
  maxConnections: 10,
  // This will be called for each crawled page
  callback: function (error, res, done) {
    if (error) {
      console.log(error)
    } else {
      var $ = res.$
      // $ is Cheerio by default
      //a lean implementation of core jQuery designed specifically for the server
      const articles = $('article.excerpt')
      const latestUpdateDate = '2020-02-10'
      let pageDate

      for (let i = 0; i < articles.get().length; i++) {
        const $article = $(articles.get(i))
        logger.log(`${i}:`)
        const data = {
          thumbnail: $article.find('img.thumb').attr('data-src'),
          href: $article.children('a').attr('href'),
          title: $article.find('header>h2>a').text(),
          date: $article.find('time').text().trim(),
        }
        logger.log(`${JSON.stringify(data)}`)
        pageDate = data.date
      }

      if (moment(latestUpdateDate).isBefore(pageDate)) {
        logger.log(`next page`)
        c.queue('https://www.sshs.xyz/tag/%E9%87%8C%E7%95%AA/2/')
      }
    }
    done()
  }
})

// Queue just one URL, with default callback
c.queue('https://www.sshs.xyz/tag/%E9%87%8C%E7%95%AA/')

// const html = fs.readFileSync('sshs.html')
// c.queue({ html })
