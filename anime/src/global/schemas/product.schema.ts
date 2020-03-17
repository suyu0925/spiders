import { Schema } from 'mongoose'

export const ProductSchema = new Schema({
  title: String, // 标题
  thumbnail: String, // 预览图网址
  magrent: String, // 磁力链接
  updateTime: Date, // 更新时间
  source: String, // 源
  exported: Boolean, // 已导出
})
