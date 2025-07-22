# 酒店预订系统 API 接口文档

## 版本信息
- **API版本**: v1.0
- **文档版本**: 1.0
- **更新日期**: 2025年7月16日
- **Base URL**: `https://api.hotel-reservation.com/api/v1`

## 认证方式
所有API接口均需要使用JWT Bearer Token进行认证：
```
Authorization: Bearer {jwt_token}
```

## 通用响应格式

### 成功响应
```json
{
    "code": 200,
    "message": "操作成功",
    "data": { ... },
    "timestamp": "2025-07-16T10:30:00Z"
}
```

### 错误响应
```json
{
    "code": 400,
    "error": "ERROR_CODE",
    "message": "错误描述",
    "details": { ... },
    "timestamp": "2025-07-16T10:30:00Z",
    "path": "/api/v1/endpoint"
}
```

## 1. 预订管理 API

### 1.1 创建预订

**请求**
```
POST /reservations
Content-Type: application/json
Authorization: Bearer {jwt_token}
```

**请求体**
```json
{
    "roomId": 1,
    "checkInDate": "2025-08-01",
    "checkOutDate": "2025-08-03",
    "guestCount": 2,
    "specialRequests": "高层房间，远离电梯",
    "paymentInfo": {
        "paymentMethod": "CREDIT_CARD",
        "cardNumber": "4532************1234",
        "cardHolderName": "张三",
        "expiryDate": "12/27",
        "cvv": "123",
        "billingAddress": {
            "street": "北京市朝阳区xxx街道",
            "city": "北京",
            "state": "北京",
            "zipCode": "100000",
            "country": "中国"
        }
    }
}
```

**响应示例**
```json
{
    "code": 200,
    "message": "预订创建成功",
    "data": {
        "reservationId": 12345,
        "confirmationNumber": "HTL20250716001",
        "status": "CONFIRMED",
        "totalAmount": 800.00,
        "currency": "CNY",
        "paymentStatus": "COMPLETED",
        "checkInDate": "2025-08-01",
        "checkOutDate": "2025-08-03",
        "room": {
            "roomId": 1,
            "roomNumber": "2001",
            "roomType": "DELUXE",
            "amenities": ["WiFi", "空调", "迷你吧", "保险箱"]
        },
        "createdAt": "2025-07-16T10:30:00Z"
    }
}
```

**错误码**
- `ROOM_NOT_AVAILABLE`: 房间不可用
- `INVALID_DATES`: 日期无效
- `PAYMENT_FAILED`: 支付失败
- `VALIDATION_ERROR`: 参数验证失败

### 1.2 查询预订详情

**请求**
```
GET /reservations/{reservationId}
Authorization: Bearer {jwt_token}
```

**路径参数**
- `reservationId` (Long): 预订ID

**响应示例**
```json
{
    "code": 200,
    "message": "查询成功",
    "data": {
        "reservationId": 12345,
        "confirmationNumber": "HTL20250716001",
        "status": "CONFIRMED",
        "userId": 1001,
        "roomId": 1,
        "checkInDate": "2025-08-01",
        "checkOutDate": "2025-08-03",
        "guestCount": 2,
        "specialRequests": "高层房间，远离电梯",
        "totalAmount": 800.00,
        "currency": "CNY",
        "createdAt": "2025-07-16T10:30:00Z",
        "updatedAt": "2025-07-16T10:30:00Z",
        "room": {
            "roomNumber": "2001",
            "roomType": "DELUXE",
            "floor": 20
        },
        "payments": [
            {
                "paymentId": 5001,
                "amount": 800.00,
                "paymentMethod": "CREDIT_CARD",
                "status": "COMPLETED",
                "transactionId": "TXN_20250716_001",
                "processedAt": "2025-07-16T10:30:15Z"
            }
        ]
    }
}
```

### 1.3 查询用户预订列表

**请求**
```
GET /reservations
Authorization: Bearer {jwt_token}
```

**查询参数**
- `page` (Integer, 可选): 页码，默认0
- `size` (Integer, 可选): 每页大小，默认10
- `status` (String, 可选): 预订状态筛选
- `fromDate` (String, 可选): 起始日期 (YYYY-MM-DD)
- `toDate` (String, 可选): 结束日期 (YYYY-MM-DD)

**响应示例**
```json
{
    "code": 200,
    "message": "查询成功",
    "data": {
        "content": [
            {
                "reservationId": 12345,
                "confirmationNumber": "HTL20250716001",
                "status": "CONFIRMED",
                "checkInDate": "2025-08-01",
                "checkOutDate": "2025-08-03",
                "totalAmount": 800.00,
                "room": {
                    "roomNumber": "2001",
                    "roomType": "DELUXE"
                }
            }
        ],
        "pageable": {
            "page": 0,
            "size": 10,
            "totalElements": 1,
            "totalPages": 1
        }
    }
}
```

### 1.4 取消预订

**请求**
```
DELETE /reservations/{reservationId}
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**请求体**
```json
{
    "reason": "行程变更",
    "requestRefund": true
}
```

**响应示例**
```json
{
    "code": 200,
    "message": "预订取消成功",
    "data": {
        "reservationId": 12345,
        "status": "CANCELLED",
        "refundAmount": 720.00,
        "refundStatus": "PROCESSING",
        "cancellationFee": 80.00,
        "cancelledAt": "2025-07-16T14:30:00Z"
    }
}
```

## 2. 房间管理 API

### 2.1 查询房间可用性

**请求**
```
GET /rooms/availability
```

**查询参数**
- `checkInDate` (String, 必需): 入住日期 (YYYY-MM-DD)
- `checkOutDate` (String, 必需): 退房日期 (YYYY-MM-DD)
- `guestCount` (Integer, 可选): 客人数量，默认1
- `roomType` (String, 可选): 房间类型筛选

**响应示例**
```json
{
    "code": 200,
    "message": "查询成功",
    "data": {
        "availableRooms": [
            {
                "roomId": 1,
                "roomNumber": "2001",
                "roomType": "DELUXE",
                "basePrice": 400.00,
                "totalPrice": 800.00,
                "maxOccupancy": 3,
                "amenities": ["WiFi", "空调", "迷你吧", "保险箱"],
                "images": [
                    "https://example.com/room1_1.jpg",
                    "https://example.com/room1_2.jpg"
                ],
                "description": "豪华双人房，配备城市景观",
                "availability": {
                    "2025-08-01": {
                        "available": true,
                        "price": 400.00
                    },
                    "2025-08-02": {
                        "available": true,
                        "price": 400.00
                    }
                }
            }
        ],
        "searchCriteria": {
            "checkInDate": "2025-08-01",
            "checkOutDate": "2025-08-03",
            "nights": 2,
            "guestCount": 2
        }
    }
}
```

### 2.2 获取房间详情

**请求**
```
GET /rooms/{roomId}
```

**响应示例**
```json
{
    "code": 200,
    "message": "查询成功",
    "data": {
        "roomId": 1,
        "roomNumber": "2001",
        "roomType": "DELUXE",
        "floor": 20,
        "basePrice": 400.00,
        "maxOccupancy": 3,
        "size": 45,
        "bedType": "King Size",
        "amenities": [
            "免费WiFi",
            "空调",
            "迷你吧",
            "保险箱",
            "电视",
            "吹风机"
        ],
        "images": [
            "https://example.com/room1_1.jpg",
            "https://example.com/room1_2.jpg",
            "https://example.com/room1_3.jpg"
        ],
        "description": "豪华双人房，配备城市景观，位于酒店高层，享受宁静舒适的住宿体验。",
        "policies": {
            "smokingAllowed": false,
            "petsAllowed": false,
            "cancellationPolicy": "24小时前免费取消"
        }
    }
}
```

### 2.3 获取房间类型列表

**请求**
```
GET /rooms/types
```

**响应示例**
```json
{
    "code": 200,
    "message": "查询成功",
    "data": [
        {
            "roomType": "STANDARD",
            "name": "标准间",
            "description": "基础设施齐全的标准双人房",
            "basePrice": 200.00,
            "maxOccupancy": 2,
            "size": 25,
            "amenities": ["WiFi", "空调", "电视"]
        },
        {
            "roomType": "DELUXE",
            "name": "豪华间",
            "description": "宽敞舒适的豪华房间",
            "basePrice": 400.00,
            "maxOccupancy": 3,
            "size": 45,
            "amenities": ["WiFi", "空调", "迷你吧", "保险箱", "电视"]
        },
        {
            "roomType": "SUITE",
            "name": "套房",
            "description": "独立客厅的豪华套房",
            "basePrice": 800.00,
            "maxOccupancy": 4,
            "size": 80,
            "amenities": ["WiFi", "空调", "迷你吧", "保险箱", "电视", "按摩浴缸"]
        }
    ]
}
```

## 3. 价格计算 API

### 3.1 计算预订价格

**请求**
```
POST /reservations/calculate-price
Content-Type: application/json
```

**请求体**
```json
{
    "roomId": 1,
    "checkInDate": "2025-08-01",
    "checkOutDate": "2025-08-03",
    "guestCount": 2,
    "discountCode": "SUMMER2025"
}
```

**响应示例**
```json
{
    "code": 200,
    "message": "价格计算成功",
    "data": {
        "breakdown": {
            "basePrice": 400.00,
            "nights": 2,
            "subtotal": 800.00,
            "taxes": [
                {
                    "name": "城市税",
                    "rate": 0.06,
                    "amount": 48.00
                }
            ],
            "fees": [
                {
                    "name": "服务费",
                    "amount": 20.00
                }
            ],
            "discounts": [
                {
                    "name": "夏季优惠",
                    "code": "SUMMER2025",
                    "amount": -80.00
                }
            ]
        },
        "total": 788.00,
        "currency": "CNY",
        "validUntil": "2025-07-16T15:30:00Z"
    }
}
```

## 4. 支付管理 API

### 4.1 查询支付详情

**请求**
```
GET /payments/{paymentId}
Authorization: Bearer {jwt_token}
```

**响应示例**
```json
{
    "code": 200,
    "message": "查询成功",
    "data": {
        "paymentId": 5001,
        "reservationId": 12345,
        "amount": 800.00,
        "currency": "CNY",
        "paymentMethod": "CREDIT_CARD",
        "status": "COMPLETED",
        "transactionId": "TXN_20250716_001",
        "cardLast4": "1234",
        "processedAt": "2025-07-16T10:30:15Z",
        "createdAt": "2025-07-16T10:30:00Z"
    }
}
```

### 4.2 申请退款

**请求**
```
POST /payments/{paymentId}/refund
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**请求体**
```json
{
    "amount": 720.00,
    "reason": "用户取消预订"
}
```

**响应示例**
```json
{
    "code": 200,
    "message": "退款申请提交成功",
    "data": {
        "refundId": 6001,
        "paymentId": 5001,
        "amount": 720.00,
        "status": "PROCESSING",
        "reason": "用户取消预订",
        "estimatedTime": "3-5个工作日",
        "createdAt": "2025-07-16T14:30:00Z"
    }
}
```

## 5. 用户管理 API

### 5.1 获取用户信息

**请求**
```
GET /users/profile
Authorization: Bearer {jwt_token}
```

**响应示例**
```json
{
    "code": 200,
    "message": "查询成功",
    "data": {
        "userId": 1001,
        "username": "zhangsan",
        "email": "zhangsan@example.com",
        "firstName": "三",
        "lastName": "张",
        "phoneNumber": "+86 138 0013 8000",
        "preferredLanguage": "zh-CN",
        "loyaltyLevel": "SILVER",
        "createdAt": "2025-01-15T09:00:00Z"
    }
}
```

### 5.2 更新用户信息

**请求**
```
PUT /users/profile
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**请求体**
```json
{
    "firstName": "三",
    "lastName": "张",
    "phoneNumber": "+86 138 0013 8000",
    "preferredLanguage": "zh-CN"
}
```

**响应示例**
```json
{
    "code": 200,
    "message": "用户信息更新成功",
    "data": {
        "userId": 1001,
        "username": "zhangsan",
        "email": "zhangsan@example.com",
        "firstName": "三",
        "lastName": "张",
        "phoneNumber": "+86 138 0013 8000",
        "preferredLanguage": "zh-CN",
        "updatedAt": "2025-07-16T11:00:00Z"
    }
}
```

## 6. 错误码说明

| 错误码 | HTTP状态码 | 描述 |
|--------|------------|------|
| VALIDATION_ERROR | 400 | 请求参数验证失败 |
| UNAUTHORIZED | 401 | 未授权访问 |
| FORBIDDEN | 403 | 没有权限执行此操作 |
| NOT_FOUND | 404 | 资源不存在 |
| ROOM_NOT_AVAILABLE | 400 | 房间在指定日期不可用 |
| INVALID_DATES | 400 | 日期参数无效 |
| PAYMENT_FAILED | 400 | 支付处理失败 |
| RESERVATION_NOT_FOUND | 404 | 预订记录不存在 |
| CANCELLATION_NOT_ALLOWED | 400 | 不允许取消预订 |
| INSUFFICIENT_INVENTORY | 400 | 库存不足 |
| DUPLICATE_RESERVATION | 400 | 重复预订 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

## 7. 限流规则

| 接口分类 | 限制 | 时间窗口 |
|----------|------|----------|
| 查询接口 | 100次/分钟 | 每个IP |
| 创建预订 | 10次/分钟 | 每个用户 |
| 支付接口 | 5次/分钟 | 每个用户 |
| 用户登录 | 5次/分钟 | 每个IP |

## 8. 接口调用示例

### JavaScript/Node.js
```javascript
const axios = require('axios');

// 创建预订
async function createReservation() {
    try {
        const response = await axios.post('https://api.hotel-reservation.com/api/v1/reservations', {
            roomId: 1,
            checkInDate: '2025-08-01',
            checkOutDate: '2025-08-03',
            guestCount: 2,
            paymentInfo: {
                paymentMethod: 'CREDIT_CARD',
                cardNumber: '4532************1234',
                // ... 其他支付信息
            }
        }, {
            headers: {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json'
            }
        });
        
        console.log('预订成功:', response.data);
    } catch (error) {
        console.error('预订失败:', error.response.data);
    }
}
```

### Python
```python
import requests

def create_reservation(token):
    url = 'https://api.hotel-reservation.com/api/v1/reservations'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        'roomId': 1,
        'checkInDate': '2025-08-01',
        'checkOutDate': '2025-08-03',
        'guestCount': 2,
        'paymentInfo': {
            'paymentMethod': 'CREDIT_CARD',
            'cardNumber': '4532************1234',
            # ... 其他支付信息
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        print('预订成功:', response.json())
    except requests.exceptions.RequestException as e:
        print('预订失败:', e)
```

### cURL
```bash
# 创建预订
curl -X POST "https://api.hotel-reservation.com/api/v1/reservations" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "roomId": 1,
    "checkInDate": "2025-08-01",
    "checkOutDate": "2025-08-03",
    "guestCount": 2,
    "paymentInfo": {
      "paymentMethod": "CREDIT_CARD",
      "cardNumber": "4532************1234",
      "cardHolderName": "张三",
      "expiryDate": "12/27",
      "cvv": "123"
    }
  }'
```

## 9. 测试环境

**测试服务器**: `https://test-api.hotel-reservation.com/api/v1`

**测试账号**:
- 用户名: `test_user`
- 密码: `Test123!`
- JWT Token: 通过登录接口获取

**测试数据**:
- 测试房间ID: 1, 2, 3
- 测试日期范围: 2025-08-01 到 2025-12-31
- 测试信用卡: 4532************1234 (总是返回成功)

---

**文档版本**: 1.0  
**最后更新**: 2025年7月16日  
**联系方式**: api-support@hotel-reservation.com
