import { Document } from 'mongoose'

export enum SourceEnum {
  sshs = '绅士会所'
}

export interface Product {
  title: string, // 标题
  thumbnail: string, // 预览图网址
  magrent: string, // 磁力链接
  updateTime: Date, // 更新时间
  source: SourceEnum, // 源
  exported: boolean, // 已导出
}

export interface ProductDoc extends Product, Document {
}
