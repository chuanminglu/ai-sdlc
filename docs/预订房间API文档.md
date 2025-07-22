# 酒店预订系统 - 预订房间API文档

## 版本信息
- **API版本**: v1.0
- **文档版本**: 1.0
- **创建日期**: 2025年7月16日
- **Base URL**: `https://api.hotel-booking.com/api/v1`

---

## API概述

预订房间功能是酒店预订系统的核心业务流程，包含以下主要API接口：

1. **房间可用性检查** - 验证房间在指定日期的可用性
2. **价格计算** - 计算预订总价格
3. **创建预订** - 创建新的预订订单
4. **支付处理** - 处理预订支付
5. **预订确认** - 确认预订并发送通知
6. **预订查询** - 查询预订详情
7. **预订取消** - 取消现有预订

---

## 认证方式

所有API接口均需要使用JWT Bearer Token进行认证：

```http
Authorization: Bearer {jwt_token}
```

**获取Token方式**:
```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "username": "user@example.com",
    "password": "password123"
}
```

---

## 通用响应格式

### 成功响应
```json
{
    "success": true,
    "code": 200,
    "message": "操作成功",
    "data": {
        // 具体数据内容
    },
    "timestamp": "2025-07-16T10:30:00Z",
    "requestId": "req_1234567890"
}
```

### 错误响应
```json
{
    "success": false,
    "code": 400,
    "error": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": {
        "field": "checkInDate",
        "reason": "入住日期不能早于今天"
    },
    "timestamp": "2025-07-16T10:30:00Z",
    "requestId": "req_1234567890"
}
```

---

## 1. 房间可用性检查

### 接口描述
检查指定房间在特定日期范围内的可用性。

### 请求信息
```http
GET /api/v1/rooms/{roomId}/availability
```

### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| roomId | Long | 是 | 房间ID |

### 查询参数
| 参数名 | 类型 | 必填 | 描述 | 示例 |
|--------|------|------|------|------|
| checkInDate | String | 是 | 入住日期 (YYYY-MM-DD) | 2025-08-01 |
| checkOutDate | String | 是 | 退房日期 (YYYY-MM-DD) | 2025-08-03 |
| guestCount | Integer | 否 | 客人数量，默认1 | 2 |

### 请求示例
```http
GET /api/v1/rooms/1/availability?checkInDate=2025-08-01&checkOutDate=2025-08-03&guestCount=2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 响应示例

**成功响应 (200)**:
```json
{
    "success": true,
    "code": 200,
    "message": "查询成功",
    "data": {
        "roomId": 1,
        "available": true,
        "dateRange": {
            "checkInDate": "2025-08-01",
            "checkOutDate": "2025-08-03",
            "nights": 2
        },
        "capacity": {
            "maxGuests": 3,
            "requestedGuests": 2,
            "available": true
        },
        "availabilityDetails": [
            {
                "date": "2025-08-01",
                "available": true,
                "status": "AVAILABLE",
                "basePrice": 400.00
            },
            {
                "date": "2025-08-02", 
                "available": true,
                "status": "AVAILABLE",
                "basePrice": 400.00
            }
        ]
    },
    "timestamp": "2025-07-16T10:30:00Z",
    "requestId": "req_availability_001"
}
```

**房间不可用 (200)**:
```json
{
    "success": true,
    "code": 200,
    "message": "查询成功",
    "data": {
        "roomId": 1,
        "available": false,
        "reason": "ALREADY_BOOKED",
        "conflictingReservations": [
            {
                "reservationId": 12345,
                "checkInDate": "2025-07-31",
                "checkOutDate": "2025-08-02"
            }
        ],
        "suggestedAlternatives": [
            {
                "roomId": 2,
                "roomNumber": "2002",
                "roomType": "DELUXE",
                "available": true,
                "basePrice": 450.00
            }
        ]
    },
    "timestamp": "2025-07-16T10:30:00Z",
    "requestId": "req_availability_002"
}
```

### 错误码
| 错误码 | HTTP状态码 | 描述 |
|--------|------------|------|
| ROOM_NOT_FOUND | 404 | 房间不存在 |
| INVALID_DATE_RANGE | 400 | 日期范围无效 |
| INVALID_GUEST_COUNT | 400 | 客人数量无效 |

---

## 2. 价格计算

### 接口描述
计算指定房间和日期的预订总价格，包含各种费用明细。

### 请求信息
```http
POST /api/v1/reservations/calculate-price
```

### 请求头
```http
Content-Type: application/json
Authorization: Bearer {jwt_token}
```

### 请求体
```json
{
    "roomId": 1,
    "checkInDate": "2025-08-01",
    "checkOutDate": "2025-08-03",
    "guestCount": 2,
    "discountCode": "SUMMER2025",
    "specialRequests": [
        "HIGH_FLOOR",
        "LATE_CHECKOUT"
    ]
}
```

### 请求体参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| roomId | Long | 是 | 房间ID |
| checkInDate | String | 是 | 入住日期 (YYYY-MM-DD) |
| checkOutDate | String | 是 | 退房日期 (YYYY-MM-DD) |
| guestCount | Integer | 是 | 客人数量 |
| discountCode | String | 否 | 优惠码 |
| specialRequests | String[] | 否 | 特殊要求 |

### 响应示例

**成功响应 (200)**:
```json
{
    "success": true,
    "code": 200,
    "message": "价格计算成功",
    "data": {
        "priceBreakdown": {
            "basePrice": 400.00,
            "nights": 2,
            "subtotal": 800.00,
            "seasonalAdjustment": {
                "rate": 0.15,
                "amount": 120.00,
                "reason": "夏季旺季"
            },
            "weekendSurcharge": {
                "rate": 0.10,
                "amount": 40.00,
                "applicableNights": 1
            },
            "taxes": [
                {
                    "name": "城市税",
                    "rate": 0.06,
                    "amount": 57.60
                },
                {
                    "name": "服务税",
                    "rate": 0.03,
                    "amount": 28.80
                }
            ],
            "fees": [
                {
                    "name": "清洁费",
                    "amount": 50.00,
                    "type": "ONE_TIME"
                }
            ],
            "discounts": [
                {
                    "name": "夏季优惠",
                    "code": "SUMMER2025",
                    "type": "PERCENTAGE",
                    "rate": 0.10,
                    "amount": -96.00,
                    "appliedTo": "SUBTOTAL"
                }
            ],
            "specialRequestFees": [
                {
                    "request": "HIGH_FLOOR",
                    "fee": 20.00
                },
                {
                    "request": "LATE_CHECKOUT",
                    "fee": 30.00
                }
            ]
        },
        "totalAmount": 1050.40,
        "currency": "CNY",
        "priceValidUntil": "2025-07-16T15:30:00Z",
        "cancellationPolicy": {
            "freeCancel": true,
            "freeCancelUntil": "2025-07-31T18:00:00Z",
            "cancellationFee": 0.00,
            "refundPolicy": "全额退款"
        }
    },
    "timestamp": "2025-07-16T10:30:00Z",
    "requestId": "req_price_001"
}
```

---

## 3. 创建预订

### 接口描述
创建新的房间预订订单。这是预订流程的核心接口。

### 请求信息
```http
POST /api/v1/reservations
```

### 请求头
```http
Content-Type: application/json
Authorization: Bearer {jwt_token}
```

### 请求体
```json
{
    "roomId": 1,
    "checkInDate": "2025-08-01",
    "checkOutDate": "2025-08-03",
    "guestInfo": {
        "primaryGuest": {
            "firstName": "张",
            "lastName": "三",
            "email": "zhangsan@example.com",
            "phone": "+86 138 0013 8000",
            "idType": "ID_CARD",
            "idNumber": "110101199001011234",
            "nationality": "CN"
        },
        "additionalGuests": [
            {
                "firstName": "李",
                "lastName": "四",
                "relationship": "SPOUSE"
            }
        ],
        "guestCount": 2
    },
    "contactInfo": {
        "email": "zhangsan@example.com",
        "phone": "+86 138 0013 8000",
        "preferredLanguage": "zh-CN",
        "notificationPreferences": ["EMAIL", "SMS"]
    },
    "specialRequests": {
        "roomPreferences": ["HIGH_FLOOR", "AWAY_FROM_ELEVATOR"],
        "accessibilityNeeds": [],
        "dietaryRequirements": [],
        "comments": "请提供安静的房间，谢谢"
    },
    "priceConfirmation": {
        "agreedAmount": 1050.40,
        "priceCalculationId": "calc_12345",
        "discountCode": "SUMMER2025"
    },
    "policies": {
        "termsAndConditionsAccepted": true,
        "privacyPolicyAccepted": true,
        "cancellationPolicyAccepted": true
    }
}
```

### 请求体参数详细说明

| 参数路径 | 类型 | 必填 | 描述 |
|----------|------|------|------|
| roomId | Long | 是 | 房间ID |
| checkInDate | String | 是 | 入住日期 |
| checkOutDate | String | 是 | 退房日期 |
| guestInfo.primaryGuest | Object | 是 | 主要客人信息 |
| guestInfo.primaryGuest.firstName | String | 是 | 名 |
| guestInfo.primaryGuest.lastName | String | 是 | 姓 |
| guestInfo.primaryGuest.email | String | 是 | 邮箱 |
| guestInfo.primaryGuest.phone | String | 是 | 电话 |
| guestInfo.primaryGuest.idType | String | 是 | 证件类型 |
| guestInfo.primaryGuest.idNumber | String | 是 | 证件号码 |
| guestInfo.additionalGuests | Array | 否 | 同行客人信息 |
| guestInfo.guestCount | Integer | 是 | 总客人数 |
| priceConfirmation.agreedAmount | BigDecimal | 是 | 确认的价格 |
| policies.termsAndConditionsAccepted | Boolean | 是 | 同意条款 |

### 响应示例

**成功响应 (201)**:
```json
{
    "success": true,
    "code": 201,
    "message": "预订创建成功",
    "data": {
        "reservationId": 12345,
        "confirmationNumber": "HTL20250716001",
        "status": "PENDING_PAYMENT",
        "roomInfo": {
            "roomId": 1,
            "roomNumber": "2001",
            "roomType": "DELUXE",
            "floor": 20
        },
        "stayInfo": {
            "checkInDate": "2025-08-01",
            "checkOutDate": "2025-08-03",
            "nights": 2,
            "guestCount": 2
        },
        "pricing": {
            "totalAmount": 1050.40,
            "currency": "CNY",
            "breakdown": {
                "roomCharges": 960.00,
                "taxes": 86.40,
                "fees": 50.00,
                "discounts": -96.00,
                "specialRequestFees": 50.00
            }
        },
        "guestInfo": {
            "primaryGuest": {
                "name": "张三",
                "email": "zhangsan@example.com",
                "phone": "+86 138 0013 8000"
            },
            "totalGuests": 2
        },
        "paymentInfo": {
            "required": true,
            "amount": 1050.40,
            "currency": "CNY",
            "paymentDeadline": "2025-07-16T11:00:00Z",
            "paymentMethods": ["ALIPAY", "WECHAT_PAY", "CREDIT_CARD"]
        },
        "policies": {
            "cancellationPolicy": {
                "freeCancel": true,
                "freeCancelUntil": "2025-07-31T18:00:00Z"
            },
            "checkInPolicy": {
                "checkInTime": "14:00",
                "lateCheckInCutoff": "23:00",
                "specialInstructions": "请在前台办理入住手续"
            }
        },
        "nextSteps": {
            "required": "PAYMENT",
            "paymentUrl": "/api/v1/payments/create",
            "timeLimit": "30分钟内完成支付"
        },
        "createdAt": "2025-07-16T10:30:00Z",
        "expiresAt": "2025-07-16T11:00:00Z"
    },
    "timestamp": "2025-07-16T10:30:00Z",
    "requestId": "req_reservation_001"
}
```

**房间不可用错误 (400)**:
```json
{
    "success": false,
    "code": 400,
    "error": "ROOM_NOT_AVAILABLE",
    "message": "所选房间在指定日期不可用",
    "details": {
        "roomId": 1,
        "requestedDates": {
            "checkInDate": "2025-08-01",
            "checkOutDate": "2025-08-03"
        },
        "conflictingReservations": [
            {
                "reservationId": 9999,
                "checkInDate": "2025-07-31",
                "checkOutDate": "2025-08-02"
            }
        ],
        "suggestedAlternatives": [
            {
                "roomId": 2,
                "roomNumber": "2002",
                "roomType": "DELUXE",
                "available": true,
                "totalPrice": 1100.00
            }
        ]
    },
    "timestamp": "2025-07-16T10:30:00Z",
    "requestId": "req_reservation_002"
}
```

---

## 4. 支付处理

### 接口描述
处理预订的支付请求。

### 请求信息
```http
POST /api/v1/payments
```

### 请求体
```json
{
    "reservationId": 12345,
    "paymentMethod": "ALIPAY",
    "amount": 1050.40,
    "currency": "CNY",
    "paymentDetails": {
        "returnUrl": "https://hotel-booking.com/payment/success",
        "notifyUrl": "https://hotel-booking.com/api/v1/payments/notify",
        "description": "酒店房间预订 - HTL20250716001"
    },
    "customerInfo": {
        "name": "张三",
        "email": "zhangsan@example.com",
        "phone": "+86 138 0013 8000"
    }
}
```

### 响应示例

**支付创建成功 (200)**:
```json
{
    "success": true,
    "code": 200,
    "message": "支付订单创建成功",
    "data": {
        "paymentId": "pay_1234567890",
        "reservationId": 12345,
        "amount": 1050.40,
        "currency": "CNY",
        "paymentMethod": "ALIPAY",
        "status": "PENDING",
        "paymentUrl": "https://qr.alipay.com/bax08431lvkzyuxd4dre001a",
        "qrCode": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
        "expireTime": "2025-07-16T11:00:00Z",
        "transactionId": null,
        "instructions": {
            "method": "使用支付宝扫描二维码完成支付",
            "timeLimit": "请在30分钟内完成支付",
            "notes": "支付完成后页面将自动跳转"
        },
        "createdAt": "2025-07-16T10:30:00Z"
    },
    "timestamp": "2025-07-16T10:30:00Z",
    "requestId": "req_payment_001"
}
```

---

## 5. 支付状态查询

### 接口描述
查询支付的当前状态。

### 请求信息
```http
GET /api/v1/payments/{paymentId}/status
```

### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| paymentId | String | 是 | 支付ID |

### 响应示例

**支付成功 (200)**:
```json
{
    "success": true,
    "code": 200,
    "message": "支付查询成功",
    "data": {
        "paymentId": "pay_1234567890",
        "reservationId": 12345,
        "status": "COMPLETED",
        "amount": 1050.40,
        "currency": "CNY",
        "paymentMethod": "ALIPAY",
        "transactionId": "2025071610300001",
        "paidAt": "2025-07-16T10:35:00Z",
        "payerInfo": {
            "account": "138****8000",
            "name": "张***"
        },
        "receipt": {
            "receiptId": "receipt_001",
            "downloadUrl": "/api/v1/payments/pay_1234567890/receipt"
        }
    },
    "timestamp": "2025-07-16T10:36:00Z",
    "requestId": "req_payment_status_001"
}
```

---

## 6. 预订确认

### 接口描述
支付成功后确认预订。通常由系统自动调用。

### 请求信息
```http
POST /api/v1/reservations/{reservationId}/confirm
```

### 响应示例

**确认成功 (200)**:
```json
{
    "success": true,
    "code": 200,
    "message": "预订确认成功",
    "data": {
        "reservationId": 12345,
        "confirmationNumber": "HTL20250716001",
        "status": "CONFIRMED",
        "confirmationDetails": {
            "confirmedAt": "2025-07-16T10:36:00Z",
            "confirmationMethod": "AUTOMATIC_AFTER_PAYMENT",
            "confirmationCode": "CONF12345"
        },
        "notifications": {
            "emailSent": true,
            "smsSent": true,
            "emailAddress": "zhangsan@example.com",
            "phoneNumber": "+86 138 0013 8000"
        },
        "checkInInstructions": {
            "checkInTime": "14:00 - 23:00",
            "location": "酒店前台",
            "requiredDocuments": ["身份证"],
            "specialInstructions": "请提前30分钟联系酒店确认到达时间",
            "contactInfo": {
                "phone": "+86 400 800 8000",
                "address": "北京市朝阳区xxx街道123号"
            }
        },
        "voucher": {
            "voucherId": "voucher_12345",
            "downloadUrl": "/api/v1/reservations/12345/voucher",
            "qrCode": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
        }
    },
    "timestamp": "2025-07-16T10:36:00Z",
    "requestId": "req_confirm_001"
}
```

---

## 7. 预订查询

### 接口描述
查询预订的详细信息。

### 请求信息
```http
GET /api/v1/reservations/{reservationId}
```

### 响应示例

**查询成功 (200)**:
```json
{
    "success": true,
    "code": 200,
    "message": "查询成功",
    "data": {
        "reservationId": 12345,
        "confirmationNumber": "HTL20250716001",
        "status": "CONFIRMED",
        "statusHistory": [
            {
                "status": "PENDING_PAYMENT",
                "timestamp": "2025-07-16T10:30:00Z",
                "note": "预订创建"
            },
            {
                "status": "CONFIRMED",
                "timestamp": "2025-07-16T10:36:00Z",
                "note": "支付成功，预订确认"
            }
        ],
        "roomInfo": {
            "roomId": 1,
            "roomNumber": "2001",
            "roomType": "DELUXE",
            "floor": 20,
            "amenities": ["WiFi", "空调", "迷你吧", "保险箱"],
            "images": [
                "https://cdn.hotel.com/rooms/room1_1.jpg",
                "https://cdn.hotel.com/rooms/room1_2.jpg"
            ]
        },
        "stayInfo": {
            "checkInDate": "2025-08-01",
            "checkOutDate": "2025-08-03",
            "nights": 2,
            "guestCount": 2,
            "checkInTime": "14:00",
            "checkOutTime": "12:00"
        },
        "guestInfo": {
            "primaryGuest": {
                "name": "张三",
                "email": "zhangsan@example.com",
                "phone": "+86 138 0013 8000"
            },
            "additionalGuests": [
                {
                    "name": "李四",
                    "relationship": "SPOUSE"
                }
            ]
        },
        "pricing": {
            "totalAmount": 1050.40,
            "currency": "CNY",
            "breakdown": {
                "basePrice": 800.00,
                "taxes": 86.40,
                "fees": 50.00,
                "discounts": -96.00,
                "extras": 50.00
            },
            "paymentStatus": "PAID",
            "paidAmount": 1050.40,
            "paidAt": "2025-07-16T10:35:00Z"
        },
        "specialRequests": {
            "requests": ["HIGH_FLOOR", "AWAY_FROM_ELEVATOR"],
            "comments": "请提供安静的房间，谢谢",
            "fulfillmentStatus": "PENDING"
        },
        "cancellationInfo": {
            "cancellable": true,
            "freeCancelUntil": "2025-07-31T18:00:00Z",
            "cancellationFee": 0.00,
            "refundAmount": 1050.40
        },
        "contactInfo": {
            "hotel": {
                "name": "城市精品酒店",
                "phone": "+86 400 800 8000",
                "address": "北京市朝阳区xxx街道123号",
                "email": "contact@hotel.com"
            }
        },
        "documents": {
            "voucher": "/api/v1/reservations/12345/voucher",
            "invoice": "/api/v1/reservations/12345/invoice",
            "receipt": "/api/v1/payments/pay_1234567890/receipt"
        },
        "createdAt": "2025-07-16T10:30:00Z",
        "updatedAt": "2025-07-16T10:36:00Z"
    },
    "timestamp": "2025-07-16T10:40:00Z",
    "requestId": "req_query_001"
}
```

---

## 8. 预订取消

### 接口描述
取消现有的预订。

### 请求信息
```http
DELETE /api/v1/reservations/{reservationId}
```

### 请求体
```json
{
    "reason": "SCHEDULE_CHANGE",
    "reasonText": "行程发生变更，无法按时入住",
    "requestRefund": true,
    "acknowledgeCancellationPolicy": true
}
```

### 响应示例

**取消成功 (200)**:
```json
{
    "success": true,
    "code": 200,
    "message": "预订取消成功",
    "data": {
        "reservationId": 12345,
        "confirmationNumber": "HTL20250716001",
        "status": "CANCELLED",
        "cancellationInfo": {
            "cancelledAt": "2025-07-16T14:30:00Z",
            "cancelledBy": "CUSTOMER",
            "reason": "SCHEDULE_CHANGE",
            "reasonText": "行程发生变更，无法按时入住"
        },
        "refundInfo": {
            "refundEligible": true,
            "originalAmount": 1050.40,
            "cancellationFee": 0.00,
            "refundAmount": 1050.40,
            "refundMethod": "ORIGINAL_PAYMENT",
            "refundStatus": "PROCESSING",
            "estimatedRefundTime": "3-7个工作日",
            "refundId": "refund_12345"
        },
        "roomInfo": {
            "roomId": 1,
            "roomNumber": "2001",
            "released": true,
            "releasedAt": "2025-07-16T14:30:00Z"
        },
        "notifications": {
            "cancellationEmailSent": true,
            "cancellationSmsSent": true
        }
    },
    "timestamp": "2025-07-16T14:30:00Z",
    "requestId": "req_cancel_001"
}
```

---

## 错误码参考

### 通用错误码
| 错误码 | HTTP状态码 | 描述 |
|--------|------------|------|
| UNAUTHORIZED | 401 | 未授权访问 |
| FORBIDDEN | 403 | 没有权限 |
| NOT_FOUND | 404 | 资源不存在 |
| VALIDATION_ERROR | 400 | 参数验证失败 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

### 业务错误码
| 错误码 | HTTP状态码 | 描述 |
|--------|------------|------|
| ROOM_NOT_AVAILABLE | 400 | 房间不可用 |
| INVALID_DATE_RANGE | 400 | 日期范围无效 |
| PRICE_CHANGED | 400 | 价格已变更 |
| PAYMENT_FAILED | 400 | 支付失败 |
| RESERVATION_NOT_FOUND | 404 | 预订不存在 |
| RESERVATION_NOT_CANCELLABLE | 400 | 预订不可取消 |
| GUEST_COUNT_EXCEEDED | 400 | 客人数量超限 |
| DUPLICATE_RESERVATION | 400 | 重复预订 |

---

## 接口调用流程

### 完整预订流程
```mermaid
sequenceDiagram
    participant C as 客户端
    participant A as API服务器
    participant P as 支付系统
    participant N as 通知服务

    C->>A: 1. 检查房间可用性
    A-->>C: 返回可用性信息
    
    C->>A: 2. 计算价格
    A-->>C: 返回价格明细
    
    C->>A: 3. 创建预订
    A-->>C: 返回预订信息(待支付)
    
    C->>A: 4. 创建支付
    A->>P: 调用支付接口
    P-->>A: 返回支付信息
    A-->>C: 返回支付链接/二维码
    
    C->>P: 5. 完成支付
    P->>A: 支付回调通知
    
    A->>A: 6. 确认预订
    A->>N: 发送确认通知
    N-->>A: 通知发送成功
    
    A-->>C: 返回预订确认
```

### 错误处理流程
1. **房间不可用**: 返回替代房间建议
2. **支付失败**: 允许重新支付或更换支付方式
3. **网络超时**: 提供支付状态查询接口
4. **价格变更**: 要求重新确认价格

---

## 限流规则

| 接口类型 | 限制频率 | 时间窗口 | 备注 |
|----------|----------|----------|------|
| 查询接口 | 100次/分钟 | 每个IP | 包括可用性查询、价格计算 |
| 预订创建 | 10次/分钟 | 每个用户 | 防止恶意预订 |
| 支付接口 | 5次/分钟 | 每个用户 | 安全限制 |
| 取消接口 | 3次/分钟 | 每个用户 | 防止误操作 |

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0 | 2025-07-16 | 初始版本 |

---

**联系方式**: api-support@hotel-booking.com  
**技术支持**: 周一至周五 9:00-18:00
