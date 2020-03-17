import { Schema } from 'mongoose'

export const SubjectSchema = new Schema({
  title: String, // 标题
  thumbnail: String, // 预览图网址
  href: String, // 详情网址
  updateTime: Date, // 更新时间
  source: String, // 源
})
