import { Document } from 'mongoose'

export enum SourceEnum {
  sshs = '绅士会所'
}

export interface Subject {
  title: string, // 标题
  thumbnail: string, // 预览图网址
  href: string, // 详情网址
  updateTime: Date, // 更新时间
  source: SourceEnum, // 源
  magnet: string, // 磁力链接
}

export interface SubjectDoc extends Subject, Document {
}
