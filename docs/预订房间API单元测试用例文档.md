# 预订房间API单元测试用例文档

## 版本信息
- **测试文档版本**: 1.0
- **创建日期**: 2025年7月16日
- **测试框架**: JUnit 5 + MockMvc + Testcontainers
- **覆盖率目标**: ≥ 85%

---

## 测试策略

### 测试分层
1. **单元测试**: 测试单个方法和类
2. **集成测试**: 测试API接口端到端
3. **契约测试**: 验证API规范一致性
4. **性能测试**: 验证响应时间和并发能力

### 测试原则
- **独立性**: 每个测试用例相互独立
- **可重复性**: 测试结果可重现
- **完整性**: 覆盖正常流程和异常情况
- **可维护性**: 测试代码清晰易维护

---

## 1. 房间可用性检查API测试

### 测试类: `RoomAvailabilityControllerTest`

#### 1.1 正常场景测试

**测试用例ID**: `TC_AVAILABILITY_001`
**测试用例名称**: 查询房间可用性-房间可用
**测试级别**: 集成测试
**优先级**: 高

```java
@Test
@DisplayName("查询房间可用性 - 房间可用")
void testCheckRoomAvailability_RoomAvailable() throws Exception {
    // Given
    Long roomId = 1L;
    String checkInDate = "2025-08-01";
    String checkOutDate = "2025-08-03";
    Integer guestCount = 2;
    
    RoomAvailabilityResponse expectedResponse = RoomAvailabilityResponse.builder()
        .roomId(roomId)
        .available(true)
        .dateRange(new DateRange(checkInDate, checkOutDate, 2))
        .capacity(new CapacityInfo(3, 2, true))
        .build();
    
    when(roomService.checkAvailability(roomId, 
        LocalDate.parse(checkInDate), 
        LocalDate.parse(checkOutDate), 
        guestCount))
        .thenReturn(expectedResponse);
    
    // When & Then
    mockMvc.perform(get("/api/v1/rooms/{roomId}/availability", roomId)
            .param("checkInDate", checkInDate)
            .param("checkOutDate", checkOutDate)
            .param("guestCount", guestCount.toString())
            .header("Authorization", "Bearer " + validJwtToken)
            .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.success").value(true))
        .andExpect(jsonPath("$.code").value(200))
        .andExpect(jsonPath("$.data.roomId").value(roomId))
        .andExpect(jsonPath("$.data.available").value(true))
        .andExpect(jsonPath("$.data.dateRange.nights").value(2))
        .andExpect(jsonPath("$.data.capacity.maxGuests").value(3))
        .andExpect(jsonPath("$.data.capacity.requestedGuests").value(2))
        .andExpect(jsonPath("$.data.capacity.available").value(true))
        .andExpect(jsonPath("$.timestamp").exists())
        .andExpect(jsonPath("$.requestId").exists());
    
    // Verify
    verify(roomService, times(1)).checkAvailability(roomId, 
        LocalDate.parse(checkInDate), 
        LocalDate.parse(checkOutDate), 
        guestCount);
}
```

**测试用例ID**: `TC_AVAILABILITY_002`
**测试用例名称**: 查询房间可用性-房间不可用
**测试级别**: 集成测试
**优先级**: 高

```java
@Test
@DisplayName("查询房间可用性 - 房间不可用")
void testCheckRoomAvailability_RoomNotAvailable() throws Exception {
    // Given
    Long roomId = 1L;
    String checkInDate = "2025-08-01";
    String checkOutDate = "2025-08-03";
    
    ConflictingReservation conflictingReservation = ConflictingReservation.builder()
        .reservationId(9999L)
        .checkInDate("2025-07-31")
        .checkOutDate("2025-08-02")
        .build();
    
    RoomAvailabilityResponse expectedResponse = RoomAvailabilityResponse.builder()
        .roomId(roomId)
        .available(false)
        .reason("ALREADY_BOOKED")
        .conflictingReservations(List.of(conflictingReservation))
        .build();
    
    when(roomService.checkAvailability(eq(roomId), any(), any(), any()))
        .thenReturn(expectedResponse);
    
    // When & Then
    mockMvc.perform(get("/api/v1/rooms/{roomId}/availability", roomId)
            .param("checkInDate", checkInDate)
            .param("checkOutDate", checkOutDate)
            .header("Authorization", "Bearer " + validJwtToken))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.success").value(true))
        .andExpect(jsonPath("$.data.available").value(false))
        .andExpect(jsonPath("$.data.reason").value("ALREADY_BOOKED"))
        .andExpect(jsonPath("$.data.conflictingReservations").isArray())
        .andExpect(jsonPath("$.data.conflictingReservations[0].reservationId").value(9999));
}
```

#### 1.2 异常场景测试

**测试用例ID**: `TC_AVAILABILITY_003`
**测试用例名称**: 查询房间可用性-房间不存在
**测试级别**: 集成测试
**优先级**: 中

```java
@Test
@DisplayName("查询房间可用性 - 房间不存在")
void testCheckRoomAvailability_RoomNotFound() throws Exception {
    // Given
    Long nonExistentRoomId = 999L;
    
    when(roomService.checkAvailability(eq(nonExistentRoomId), any(), any(), any()))
        .thenThrow(new RoomNotFoundException(nonExistentRoomId));
    
    // When & Then
    mockMvc.perform(get("/api/v1/rooms/{roomId}/availability", nonExistentRoomId)
            .param("checkInDate", "2025-08-01")
            .param("checkOutDate", "2025-08-03")
            .header("Authorization", "Bearer " + validJwtToken))
        .andExpected(status().isNotFound())
        .andExpected(jsonPath("$.success").value(false))
        .andExpected(jsonPath("$.error").value("ROOM_NOT_FOUND"))
        .andExpected(jsonPath("$.message").value("房间不存在"));
}
```

**测试用例ID**: `TC_AVAILABILITY_004`
**测试用例名称**: 查询房间可用性-日期参数无效
**测试级别**: 集成测试
**优先级**: 高

```java
@Test
@DisplayName("查询房间可用性 - 日期参数无效")
void testCheckRoomAvailability_InvalidDateRange() throws Exception {
    // Given - 退房日期早于入住日期
    Long roomId = 1L;
    String checkInDate = "2025-08-03";
    String checkOutDate = "2025-08-01";
    
    // When & Then
    mockMvc.perform(get("/api/v1/rooms/{roomId}/availability", roomId)
            .param("checkInDate", checkInDate)
            .param("checkOutDate", checkOutDate)
            .header("Authorization", "Bearer " + validJwtToken))
        .andExpect(status().isBadRequest())
        .andExpected(jsonPath("$.success").value(false))
        .andExpected(jsonPath("$.error").value("INVALID_DATE_RANGE"))
        .andExpected(jsonPath("$.message").contains("退房日期必须晚于入住日期"));
}
```

**测试用例ID**: `TC_AVAILABILITY_005`
**测试用例名称**: 查询房间可用性-未授权访问
**测试级别**: 集成测试
**优先级**: 高

```java
@Test
@DisplayName("查询房间可用性 - 未授权访问")
void testCheckRoomAvailability_Unauthorized() throws Exception {
    // When & Then
    mockMvc.perform(get("/api/v1/rooms/{roomId}/availability", 1L)
            .param("checkInDate", "2025-08-01")
            .param("checkOutDate", "2025-08-03"))
        .andExpect(status().isUnauthorized())
        .andExpected(jsonPath("$.success").value(false))
        .andExpected(jsonPath("$.error").value("UNAUTHORIZED"));
}
```

---

## 2. 价格计算API测试

### 测试类: `PriceCalculationControllerTest`

#### 2.1 正常场景测试

**测试用例ID**: `TC_PRICE_001`
**测试用例名称**: 计算预订价格-基础价格计算
**测试级别**: 集成测试
**优先级**: 高

```java
@Test
@DisplayName("计算预订价格 - 基础价格计算")
void testCalculatePrice_BasicPricing() throws Exception {
    // Given
    PriceCalculationRequest request = PriceCalculationRequest.builder()
        .roomId(1L)
        .checkInDate("2025-08-01")
        .checkOutDate("2025-08-03")
        .guestCount(2)
        .build();
    
    PriceBreakdown expectedBreakdown = PriceBreakdown.builder()
        .basePrice(BigDecimal.valueOf(400.00))
        .nights(2)
        .subtotal(BigDecimal.valueOf(800.00))
        .taxes(List.of(
            Tax.builder().name("城市税").rate(0.06).amount(BigDecimal.valueOf(48.00)).build()
        ))
        .totalAmount(BigDecimal.valueOf(848.00))
        .currency("CNY")
        .build();
    
    when(priceService.calculatePrice(any(PriceCalculationRequest.class)))
        .thenReturn(expectedBreakdown);
    
    // When & Then
    mockMvc.perform(post("/api/v1/reservations/calculate-price")
            .content(objectMapper.writeValueAsString(request))
            .header("Authorization", "Bearer " + validJwtToken)
            .contentType(MediaType.APPLICATION_JSON))
        .andExpected(status().isOk())
        .andExpected(jsonPath("$.success").value(true))
        .andExpected(jsonPath("$.data.priceBreakdown.basePrice").value(400.00))
        .andExpected(jsonPath("$.data.priceBreakdown.nights").value(2))
        .andExpected(jsonPath("$.data.priceBreakdown.subtotal").value(800.00))
        .andExpected(jsonPath("$.data.totalAmount").value(848.00))
        .andExpected(jsonPath("$.data.currency").value("CNY"));
}
```

**测试用例ID**: `TC_PRICE_002`
**测试用例名称**: 计算预订价格-包含折扣和额外费用
**测试级别**: 集成测试
**优先级**: 高

```java
@Test
@DisplayName("计算预订价格 - 包含折扣和额外费用")
void testCalculatePrice_WithDiscountsAndFees() throws Exception {
    // Given
    PriceCalculationRequest request = PriceCalculationRequest.builder()
        .roomId(1L)
        .checkInDate("2025-08-01")
        .checkOutDate("2025-08-03")
        .guestCount(2)
        .discountCode("SUMMER2025")
        .specialRequests(List.of("HIGH_FLOOR", "LATE_CHECKOUT"))
        .build();
    
    PriceBreakdown expectedBreakdown = PriceBreakdown.builder()
        .basePrice(BigDecimal.valueOf(400.00))
        .nights(2)
        .subtotal(BigDecimal.valueOf(800.00))
        .discounts(List.of(
            Discount.builder()
                .name("夏季优惠")
                .code("SUMMER2025")
                .type("PERCENTAGE")
                .rate(0.10)
                .amount(BigDecimal.valueOf(-80.00))
                .build()
        ))
        .specialRequestFees(List.of(
            SpecialRequestFee.builder().request("HIGH_FLOOR").fee(BigDecimal.valueOf(20.00)).build(),
            SpecialRequestFee.builder().request("LATE_CHECKOUT").fee(BigDecimal.valueOf(30.00)).build()
        ))
        .totalAmount(BigDecimal.valueOf(818.00))
        .build();
    
    when(priceService.calculatePrice(any(PriceCalculationRequest.class)))
        .thenReturn(expectedBreakdown);
    
    // When & Then
    mockMvc.perform(post("/api/v1/reservations/calculate-price")
            .content(objectMapper.writeValueAsString(request))
            .header("Authorization", "Bearer " + validJwtToken)
            .contentType(MediaType.APPLICATION_JSON))
        .andExpected(status().isOk())
        .andExpected(jsonPath("$.data.priceBreakdown.discounts[0].code").value("SUMMER2025"))
        .andExpected(jsonPath("$.data.priceBreakdown.discounts[0].amount").value(-80.00))
        .andExpected(jsonPath("$.data.priceBreakdown.specialRequestFees").isArray())
        .andExpected(jsonPath("$.data.priceBreakdown.specialRequestFees", hasSize(2)))
        .andExpected(jsonPath("$.data.totalAmount").value(818.00));
}
```

#### 2.2 异常场景测试

**测试用例ID**: `TC_PRICE_003`
**测试用例名称**: 计算预订价格-无效折扣码
**测试级别**: 集成测试
**优先级**: 中

```java
@Test
@DisplayName("计算预订价格 - 无效折扣码")
void testCalculatePrice_InvalidDiscountCode() throws Exception {
    // Given
    PriceCalculationRequest request = PriceCalculationRequest.builder()
        .roomId(1L)
        .checkInDate("2025-08-01")
        .checkOutDate("2025-08-03")
        .guestCount(2)
        .discountCode("INVALID_CODE")
        .build();
    
    when(priceService.calculatePrice(any(PriceCalculationRequest.class)))
        .thenThrow(new InvalidDiscountCodeException("INVALID_CODE"));
    
    // When & Then
    mockMvc.perform(post("/api/v1/reservations/calculate-price")
            .content(objectMapper.writeValueAsString(request))
            .header("Authorization", "Bearer " + validJwtToken)
            .contentType(MediaType.APPLICATION_JSON))
        .andExpected(status().isBadRequest())
        .andExpected(jsonPath("$.success").value(false))
        .andExpected(jsonPath("$.error").value("INVALID_DISCOUNT_CODE"))
        .andExpected(jsonPath("$.message").contains("折扣码无效"));
}
```

---

## 3. 创建预订API测试

### 测试类: `ReservationCreationControllerTest`

#### 3.1 正常场景测试

**测试用例ID**: `TC_RESERVATION_001`
**测试用例名称**: 创建预订-完整信息
**测试级别**: 集成测试
**优先级**: 高

```java
@Test
@DisplayName("创建预订 - 完整信息")
void testCreateReservation_CompleteInformation() throws Exception {
    // Given
    CreateReservationRequest request = CreateReservationRequest.builder()
        .roomId(1L)
        .checkInDate("2025-08-01")
        .checkOutDate("2025-08-03")
        .guestInfo(GuestInfo.builder()
            .primaryGuest(PrimaryGuest.builder()
                .firstName("张")
                .lastName("三")
                .email("zhangsan@example.com")
                .phone("+86 138 0013 8000")
                .idType("ID_CARD")
                .idNumber("110101199001011234")
                .build())
            .guestCount(2)
            .build())
        .priceConfirmation(PriceConfirmation.builder()
            .agreedAmount(BigDecimal.valueOf(1050.40))
            .build())
        .policies(PolicyAcceptance.builder()
            .termsAndConditionsAccepted(true)
            .privacyPolicyAccepted(true)
            .cancellationPolicyAccepted(true)
            .build())
        .build();
    
    ReservationResponse expectedResponse = ReservationResponse.builder()
        .reservationId(12345L)
        .confirmationNumber("HTL20250716001")
        .status("PENDING_PAYMENT")
        .totalAmount(BigDecimal.valueOf(1050.40))
        .paymentRequired(true)
        .build();
    
    when(reservationService.createReservation(any(CreateReservationRequest.class), any()))
        .thenReturn(expectedResponse);
    
    // When & Then
    mockMvc.perform(post("/api/v1/reservations")
            .content(objectMapper.writeValueAsString(request))
            .header("Authorization", "Bearer " + validJwtToken)
            .contentType(MediaType.APPLICATION_JSON))
        .andExpected(status().isCreated())
        .andExpected(jsonPath("$.success").value(true))
        .andExpected(jsonPath("$.code").value(201))
        .andExpected(jsonPath("$.data.reservationId").value(12345))
        .andExpected(jsonPath("$.data.confirmationNumber").value("HTL20250716001"))
        .andExpected(jsonPath("$.data.status").value("PENDING_PAYMENT"))
        .andExpected(jsonPath("$.data.totalAmount").value(1050.40))
        .andExpected(jsonPath("$.data.paymentInfo.required").value(true));
    
    // Verify
    verify(reservationService, times(1)).createReservation(any(), any());
    verifyNoInteractions(paymentService);
}
```

#### 3.2 数据验证测试

**测试用例ID**: `TC_RESERVATION_002`
**测试用例名称**: 创建预订-必填字段缺失
**测试级别**: 集成测试
**优先级**: 高

```java
@Test
@DisplayName("创建预订 - 必填字段缺失")
void testCreateReservation_RequiredFieldsMissing() throws Exception {
    // Given - 缺少必填字段的请求
    CreateReservationRequest request = CreateReservationRequest.builder()
        .roomId(null) // 缺少房间ID
        .checkInDate("2025-08-01")
        // 缺少退房日期
        .guestInfo(GuestInfo.builder()
            .primaryGuest(PrimaryGuest.builder()
                .firstName("张")
                // 缺少姓氏
                .email("invalid-email") // 无效邮箱格式
                .build())
            .build())
        .build();
    
    // When & Then
    mockMvc.perform(post("/api/v1/reservations")
            .content(objectMapper.writeValueAsString(request))
            .header("Authorization", "Bearer " + validJwtToken)
            .contentType(MediaType.APPLICATION_JSON))
        .andExpected(status().isBadRequest())
        .andExpected(jsonPath("$.success").value(false))
        .andExpected(jsonPath("$.error").value("VALIDATION_ERROR"))
        .andExpected(jsonPath("$.details").isArray())
        .andExpected(jsonPath("$.details[*].field", 
            hasItems("roomId", "checkOutDate", "guestInfo.primaryGuest.lastName", "guestInfo.primaryGuest.email")));
    
    // Verify - 服务层不应被调用
    verifyNoInteractions(reservationService);
}
```

**测试用例ID**: `TC_RESERVATION_003`
**测试用例名称**: 创建预订-客人数量超过房间容量
**测试级别**: 集成测试
**优先级**: 高

```java
@Test
@DisplayName("创建预订 - 客人数量超过房间容量")
void testCreateReservation_GuestCountExceedsCapacity() throws Exception {
    // Given
    CreateReservationRequest request = createValidReservationRequest();
    request.getGuestInfo().setGuestCount(5); // 超过房间容量
    
    when(reservationService.createReservation(any(), any()))
        .thenThrow(new GuestCountExceededException(5, 3));
    
    // When & Then
    mockMvc.perform(post("/api/v1/reservations")
            .content(objectMapper.writeValueAsString(request))
            .header("Authorization", "Bearer " + validJwtToken)
            .contentType(MediaType.APPLICATION_JSON))
        .andExpected(status().isBadRequest())
        .andExpected(jsonPath("$.success").value(false))
        .andExpected(jsonPath("$.error").value("GUEST_COUNT_EXCEEDED"))
        .andExpected(jsonPath("$.details.requestedGuests").value(5))
        .andExpected(jsonPath("$.details.maxCapacity").value(3));
}
```

#### 3.3 业务逻辑测试

**测试用例ID**: `TC_RESERVATION_004`
**测试用例名称**: 创建预订-房间已被预订
**测试级别**: 集成测试
**优先级**: 高

```java
@Test
@DisplayName("创建预订 - 房间已被预订")
void testCreateReservation_RoomAlreadyBooked() throws Exception {
    // Given
    CreateReservationRequest request = createValidReservationRequest();
    
    when(reservationService.createReservation(any(), any()))
        .thenThrow(new RoomNotAvailableException(1L, 
            new DateRange("2025-08-01", "2025-08-03")));
    
    // When & Then
    mockMvc.perform(post("/api/v1/reservations")
            .content(objectMapper.writeValueAsString(request))
            .header("Authorization", "Bearer " + validJwtToken)
            .contentType(MediaType.APPLICATION_JSON))
        .andExpected(status().isBadRequest())
        .andExpected(jsonPath("$.success").value(false))
        .andExpected(jsonPath("$.error").value("ROOM_NOT_AVAILABLE"))
        .andExpected(jsonPath("$.details.roomId").value(1))
        .andExpected(jsonPath("$.details.requestedDates.checkInDate").value("2025-08-01"))
        .andExpected(jsonPath("$.details.suggestedAlternatives").isArray());
}
```

---

## 4. 支付处理API测试

### 测试类: `PaymentControllerTest`

#### 4.1 正常场景测试

**测试用例ID**: `TC_PAYMENT_001`
**测试用例名称**: 创建支付-支付宝支付
**测试级别**: 集成测试
**优先级**: 高

```java
@Test
@DisplayName("创建支付 - 支付宝支付")
void testCreatePayment_AlipaySuccess() throws Exception {
    // Given
    CreatePaymentRequest request = CreatePaymentRequest.builder()
        .reservationId(12345L)
        .paymentMethod("ALIPAY")
        .amount(BigDecimal.valueOf(1050.40))
        .currency("CNY")
        .build();
    
    PaymentResponse expectedResponse = PaymentResponse.builder()
        .paymentId("pay_1234567890")
        .reservationId(12345L)
        .status("PENDING")
        .paymentUrl("https://qr.alipay.com/bax08431lvkzyuxd4dre001a")
        .qrCode("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...")
        .expireTime("2025-07-16T11:00:00Z")
        .build();
    
    when(paymentService.createPayment(any(CreatePaymentRequest.class)))
        .thenReturn(expectedResponse);
    
    // When & Then
    mockMvc.perform(post("/api/v1/payments")
            .content(objectMapper.writeValueAsString(request))
            .header("Authorization", "Bearer " + validJwtToken)
            .contentType(MediaType.APPLICATION_JSON))
        .andExpected(status().isOk())
        .andExpected(jsonPath("$.success").value(true))
        .andExpected(jsonPath("$.data.paymentId").value("pay_1234567890"))
        .andExpected(jsonPath("$.data.status").value("PENDING"))
        .andExpected(jsonPath("$.data.paymentUrl").exists())
        .andExpected(jsonPath("$.data.qrCode").exists())
        .andExpected(jsonPath("$.data.expireTime").exists());
}
```

**测试用例ID**: `TC_PAYMENT_002`
**测试用例名称**: 查询支付状态-支付成功
**测试级别**: 集成测试
**优先级**: 高

```java
@Test
@DisplayName("查询支付状态 - 支付成功")
void testGetPaymentStatus_PaymentCompleted() throws Exception {
    // Given
    String paymentId = "pay_1234567890";
    
    PaymentStatusResponse expectedResponse = PaymentStatusResponse.builder()
        .paymentId(paymentId)
        .reservationId(12345L)
        .status("COMPLETED")
        .amount(BigDecimal.valueOf(1050.40))
        .transactionId("2025071610300001")
        .paidAt("2025-07-16T10:35:00Z")
        .build();
    
    when(paymentService.getPaymentStatus(paymentId))
        .thenReturn(expectedResponse);
    
    // When & Then
    mockMvc.perform(get("/api/v1/payments/{paymentId}/status", paymentId)
            .header("Authorization", "Bearer " + validJwtToken))
        .andExpected(status().isOk())
        .andExpected(jsonPath("$.success").value(true))
        .andExpected(jsonPath("$.data.paymentId").value(paymentId))
        .andExpected(jsonPath("$.data.status").value("COMPLETED"))
        .andExpected(jsonPath("$.data.transactionId").value("2025071610300001"))
        .andExpected(jsonPath("$.data.paidAt").exists());
}
```

#### 4.2 异常场景测试

**测试用例ID**: `TC_PAYMENT_003`
**测试用例名称**: 创建支付-预订不存在
**测试级别**: 集成测试
**优先级**: 高

```java
@Test
@DisplayName("创建支付 - 预订不存在")
void testCreatePayment_ReservationNotFound() throws Exception {
    // Given
    CreatePaymentRequest request = CreatePaymentRequest.builder()
        .reservationId(99999L) // 不存在的预订ID
        .paymentMethod("ALIPAY")
        .amount(BigDecimal.valueOf(1050.40))
        .build();
    
    when(paymentService.createPayment(any()))
        .thenThrow(new ReservationNotFoundException(99999L));
    
    // When & Then
    mockMvc.perform(post("/api/v1/payments")
            .content(objectMapper.writeValueAsString(request))
            .header("Authorization", "Bearer " + validJwtToken)
            .contentType(MediaType.APPLICATION_JSON))
        .andExpected(status().isNotFound())
        .andExpected(jsonPath("$.success").value(false))
        .andExpected(jsonPath("$.error").value("RESERVATION_NOT_FOUND"))
        .andExpected(jsonPath("$.details.reservationId").value(99999));
}
```

---

## 5. 预订查询API测试

### 测试类: `ReservationQueryControllerTest`

**测试用例ID**: `TC_QUERY_001`
**测试用例名称**: 查询预订详情-预订存在
**测试级别**: 集成测试
**优先级**: 高

```java
@Test
@DisplayName("查询预订详情 - 预订存在")
void testGetReservationDetails_ReservationExists() throws Exception {
    // Given
    Long reservationId = 12345L;
    
    ReservationDetailResponse expectedResponse = ReservationDetailResponse.builder()
        .reservationId(reservationId)
        .confirmationNumber("HTL20250716001")
        .status("CONFIRMED")
        .roomInfo(RoomInfo.builder()
            .roomId(1L)
            .roomNumber("2001")
            .roomType("DELUXE")
            .build())
        .stayInfo(StayInfo.builder()
            .checkInDate("2025-08-01")
            .checkOutDate("2025-08-03")
            .nights(2)
            .build())
        .totalAmount(BigDecimal.valueOf(1050.40))
        .build();
    
    when(reservationService.getReservationDetails(reservationId, getCurrentUserId()))
        .thenReturn(expectedResponse);
    
    // When & Then
    mockMvc.perform(get("/api/v1/reservations/{reservationId}", reservationId)
            .header("Authorization", "Bearer " + validJwtToken))
        .andExpected(status().isOk())
        .andExpected(jsonPath("$.success").value(true))
        .andExpected(jsonPath("$.data.reservationId").value(reservationId))
        .andExpected(jsonPath("$.data.confirmationNumber").value("HTL20250716001"))
        .andExpected(jsonPath("$.data.status").value("CONFIRMED"))
        .andExpected(jsonPath("$.data.roomInfo.roomNumber").value("2001"))
        .andExpected(jsonPath("$.data.stayInfo.nights").value(2));
}
```

---

## 6. 预订取消API测试

### 测试类: `ReservationCancellationControllerTest`

**测试用例ID**: `TC_CANCEL_001`
**测试用例名称**: 取消预订-正常取消
**测试级别**: 集成测试
**优先级**: 高

```java
@Test
@DisplayName("取消预订 - 正常取消")
void testCancelReservation_NormalCancellation() throws Exception {
    // Given
    Long reservationId = 12345L;
    
    CancelReservationRequest request = CancelReservationRequest.builder()
        .reason("SCHEDULE_CHANGE")
        .reasonText("行程发生变更")
        .requestRefund(true)
        .acknowledgeCancellationPolicy(true)
        .build();
    
    CancellationResponse expectedResponse = CancellationResponse.builder()
        .reservationId(reservationId)
        .status("CANCELLED")
        .refundAmount(BigDecimal.valueOf(1050.40))
        .refundStatus("PROCESSING")
        .estimatedRefundTime("3-7个工作日")
        .build();
    
    when(reservationService.cancelReservation(eq(reservationId), any(), any()))
        .thenReturn(expectedResponse);
    
    // When & Then
    mockMvc.perform(delete("/api/v1/reservations/{reservationId}", reservationId)
            .content(objectMapper.writeValueAsString(request))
            .header("Authorization", "Bearer " + validJwtToken)
            .contentType(MediaType.APPLICATION_JSON))
        .andExpected(status().isOk())
        .andExpected(jsonPath("$.success").value(true))
        .andExpected(jsonPath("$.data.status").value("CANCELLED"))
        .andExpected(jsonPath("$.data.refundAmount").value(1050.40))
        .andExpected(jsonPath("$.data.refundStatus").value("PROCESSING"));
}
```

---

## 7. 服务层单元测试

### 测试类: `ReservationServiceTest`

#### 7.1 核心业务逻辑测试

**测试用例ID**: `TC_SERVICE_001`
**测试用例名称**: 预订服务-创建预订业务逻辑
**测试级别**: 单元测试
**优先级**: 高

```java
@ExtendWith(MockitoExtension.class)
class ReservationServiceTest {
    
    @Mock
    private RoomService roomService;
    
    @Mock
    private PaymentService paymentService;
    
    @Mock
    private NotificationService notificationService;
    
    @Mock
    private ReservationRepository reservationRepository;
    
    @InjectMocks
    private ReservationServiceImpl reservationService;
    
    @Test
    @DisplayName("创建预订 - 正常流程")
    void testCreateReservation_NormalFlow() {
        // Given
        CreateReservationRequest request = createValidRequest();
        Long userId = 1L;
        
        Room room = Room.builder()
            .id(1L)
            .roomNumber("2001")
            .maxOccupancy(3)
            .basePrice(BigDecimal.valueOf(400))
            .status(RoomStatus.AVAILABLE)
            .build();
        
        when(roomService.findById(1L)).thenReturn(room);
        when(roomService.checkAvailability(any(), any(), any(), any())).thenReturn(true);
        when(roomService.lockRoom(any(), any(), any())).thenReturn(true);
        when(reservationRepository.save(any())).thenAnswer(invocation -> {
            Reservation reservation = invocation.getArgument(0);
            reservation.setId(12345L);
            return reservation;
        });
        
        // When
        ReservationResponse response = reservationService.createReservation(request, userId);
        
        // Then
        assertThat(response).isNotNull();
        assertThat(response.getReservationId()).isEqualTo(12345L);
        assertThat(response.getStatus()).isEqualTo("PENDING_PAYMENT");
        assertThat(response.getTotalAmount()).isEqualTo(request.getPriceConfirmation().getAgreedAmount());
        
        // Verify interactions
        verify(roomService).checkAvailability(1L, 
            LocalDate.parse(request.getCheckInDate()), 
            LocalDate.parse(request.getCheckOutDate()), 
            request.getGuestInfo().getGuestCount());
        verify(roomService).lockRoom(eq(1L), any(), any());
        verify(reservationRepository).save(any(Reservation.class));
        verifyNoInteractions(paymentService); // 此阶段不应调用支付服务
    }
    
    @Test
    @DisplayName("创建预订 - 房间不可用")
    void testCreateReservation_RoomNotAvailable() {
        // Given
        CreateReservationRequest request = createValidRequest();
        Long userId = 1L;
        
        when(roomService.findById(1L)).thenReturn(createRoom());
        when(roomService.checkAvailability(any(), any(), any(), any())).thenReturn(false);
        
        // When & Then
        assertThatThrownBy(() -> reservationService.createReservation(request, userId))
            .isInstanceOf(RoomNotAvailableException.class)
            .hasMessageContaining("房间不可用");
        
        // Verify
        verify(roomService, never()).lockRoom(any(), any(), any());
        verify(reservationRepository, never()).save(any());
    }
    
    @Test
    @DisplayName("创建预订 - 客人数量超过容量")
    void testCreateReservation_GuestCountExceeded() {
        // Given
        CreateReservationRequest request = createValidRequest();
        request.getGuestInfo().setGuestCount(5); // 超过房间容量
        Long userId = 1L;
        
        Room room = createRoom();
        room.setMaxOccupancy(3);
        
        when(roomService.findById(1L)).thenReturn(room);
        
        // When & Then
        assertThatThrownBy(() -> reservationService.createReservation(request, userId))
            .isInstanceOf(GuestCountExceededException.class)
            .hasMessageContaining("客人数量超过房间容量");
    }
}
```

### 测试类: `PriceCalculationServiceTest`

**测试用例ID**: `TC_PRICE_SERVICE_001`
**测试用例名称**: 价格计算服务-基础价格计算
**测试级别**: 单元测试
**优先级**: 高

```java
@Test
@DisplayName("价格计算 - 基础价格计算")
void testCalculatePrice_BasicCalculation() {
    // Given
    PriceCalculationRequest request = PriceCalculationRequest.builder()
        .roomId(1L)
        .checkInDate("2025-08-01")
        .checkOutDate("2025-08-03")
        .guestCount(2)
        .build();
    
    Room room = Room.builder()
        .id(1L)
        .basePrice(BigDecimal.valueOf(400))
        .build();
    
    when(roomService.findById(1L)).thenReturn(room);
    
    // When
    PriceBreakdown result = priceCalculationService.calculatePrice(request);
    
    // Then
    assertThat(result.getBasePrice()).isEqualByComparingTo(BigDecimal.valueOf(400));
    assertThat(result.getNights()).isEqualTo(2);
    assertThat(result.getSubtotal()).isEqualByComparingTo(BigDecimal.valueOf(800));
    assertThat(result.getTotalAmount()).isGreaterThan(BigDecimal.valueOf(800)); // 包含税费
}

@Test
@DisplayName("价格计算 - 季节性调价")
void testCalculatePrice_SeasonalPricing() {
    // Given
    PriceCalculationRequest request = PriceCalculationRequest.builder()
        .roomId(1L)
        .checkInDate("2025-07-01") // 夏季旺季
        .checkOutDate("2025-07-03")
        .guestCount(2)
        .build();
    
    Room room = Room.builder()
        .id(1L)
        .basePrice(BigDecimal.valueOf(400))
        .build();
    
    when(roomService.findById(1L)).thenReturn(room);
    
    // When
    PriceBreakdown result = priceCalculationService.calculatePrice(request);
    
    // Then
    assertThat(result.getSeasonalAdjustment()).isNotNull();
    assertThat(result.getSeasonalAdjustment().getRate()).isEqualTo(0.15); // 15%涨价
    assertThat(result.getSeasonalAdjustment().getAmount()).isEqualByComparingTo(BigDecimal.valueOf(120)); // 800 * 0.15
}
```

---

## 8. 数据访问层测试

### 测试类: `ReservationRepositoryTest`

**测试用例ID**: `TC_REPO_001`
**测试用例名称**: 预订仓储-查询重叠预订
**测试级别**: 集成测试
**优先级**: 高

```java
@DataJpaTest
@TestPropertySource(locations = "classpath:application-test.properties")
class ReservationRepositoryTest {
    
    @Autowired
    private TestEntityManager entityManager;
    
    @Autowired
    private ReservationRepository reservationRepository;
    
    @Test
    @DisplayName("查询重叠预订 - 存在重叠")
    void testFindOverlappingReservations_OverlappingExists() {
        // Given
        Long roomId = 1L;
        LocalDate checkIn = LocalDate.of(2025, 8, 1);
        LocalDate checkOut = LocalDate.of(2025, 8, 3);
        
        // 创建测试数据 - 重叠的预订
        Reservation existingReservation = Reservation.builder()
            .roomId(roomId)
            .checkInDate(LocalDate.of(2025, 7, 31))
            .checkOutDate(LocalDate.of(2025, 8, 2))
            .status(ReservationStatus.CONFIRMED)
            .totalAmount(BigDecimal.valueOf(800))
            .userId(100L)
            .build();
        
        entityManager.persistAndFlush(existingReservation);
        
        // When
        List<Reservation> overlappingReservations = reservationRepository
            .findOverlappingReservations(roomId, checkIn, checkOut);
        
        // Then
        assertThat(overlappingReservations).hasSize(1);
        assertThat(overlappingReservations.get(0).getRoomId()).isEqualTo(roomId);
        assertThat(overlappingReservations.get(0).getStatus()).isEqualTo(ReservationStatus.CONFIRMED);
    }
    
    @Test
    @DisplayName("查询重叠预订 - 无重叠")
    void testFindOverlappingReservations_NoOverlapping() {
        // Given
        Long roomId = 1L;
        LocalDate checkIn = LocalDate.of(2025, 8, 5);
        LocalDate checkOut = LocalDate.of(2025, 8, 7);
        
        // 创建测试数据 - 不重叠的预订
        Reservation existingReservation = Reservation.builder()
            .roomId(roomId)
            .checkInDate(LocalDate.of(2025, 8, 1))
            .checkOutDate(LocalDate.of(2025, 8, 3))
            .status(ReservationStatus.CONFIRMED)
            .totalAmount(BigDecimal.valueOf(800))
            .userId(100L)
            .build();
        
        entityManager.persistAndFlush(existingReservation);
        
        // When
        List<Reservation> overlappingReservations = reservationRepository
            .findOverlappingReservations(roomId, checkIn, checkOut);
        
        // Then
        assertThat(overlappingReservations).isEmpty();
    }
}
```

---

## 9. 性能测试

### 测试类: `ReservationPerformanceTest`

**测试用例ID**: `TC_PERF_001`
**测试用例名称**: 预订API性能测试
**测试级别**: 性能测试
**优先级**: 中

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class ReservationPerformanceTest {
    
    @Autowired
    private TestRestTemplate restTemplate;
    
    @Test
    @DisplayName("创建预订 - 响应时间测试")
    @Timeout(value = 5, unit = TimeUnit.SECONDS)
    void testCreateReservation_ResponseTime() {
        // Given
        CreateReservationRequest request = createValidRequest();
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(getValidJwtToken());
        HttpEntity<CreateReservationRequest> entity = new HttpEntity<>(request, headers);
        
        // When
        long startTime = System.currentTimeMillis();
        ResponseEntity<ApiResponse<ReservationResponse>> response = restTemplate.postForEntity(
            "/api/v1/reservations", entity, 
            new ParameterizedTypeReference<ApiResponse<ReservationResponse>>() {});
        long endTime = System.currentTimeMillis();
        
        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(endTime - startTime).isLessThan(3000); // 响应时间小于3秒
    }
    
    @Test
    @DisplayName("并发预订测试")
    void testConcurrentReservations() throws InterruptedException {
        // Given
        int threadCount = 10;
        CountDownLatch latch = new CountDownLatch(threadCount);
        List<CompletableFuture<ResponseEntity<String>>> futures = new ArrayList<>();
        
        // When
        for (int i = 0; i < threadCount; i++) {
            CompletableFuture<ResponseEntity<String>> future = CompletableFuture.supplyAsync(() -> {
                try {
                    CreateReservationRequest request = createValidRequest();
                    request.setRoomId((long) (i % 5 + 1)); // 分散到不同房间
                    
                    HttpHeaders headers = new HttpHeaders();
                    headers.setBearerAuth(getValidJwtToken());
                    HttpEntity<CreateReservationRequest> entity = new HttpEntity<>(request, headers);
                    
                    return restTemplate.postForEntity("/api/v1/reservations", entity, String.class);
                } finally {
                    latch.countDown();
                }
            });
            futures.add(future);
        }
        
        // Then
        latch.await(30, TimeUnit.SECONDS);
        
        long successCount = futures.stream()
            .map(CompletableFuture::join)
            .filter(response -> response.getStatusCode().is2xxSuccessful())
            .count();
        
        assertThat(successCount).isGreaterThan(threadCount * 0.8); // 至少80%成功率
    }
}
```

---

## 10. 测试数据管理

### 测试数据工厂类

```java
@Component
public class TestDataFactory {
    
    public static CreateReservationRequest createValidReservationRequest() {
        return CreateReservationRequest.builder()
            .roomId(1L)
            .checkInDate("2025-08-01")
            .checkOutDate("2025-08-03")
            .guestInfo(GuestInfo.builder()
                .primaryGuest(createPrimaryGuest())
                .guestCount(2)
                .build())
            .priceConfirmation(PriceConfirmation.builder()
                .agreedAmount(BigDecimal.valueOf(1050.40))
                .build())
            .policies(PolicyAcceptance.builder()
                .termsAndConditionsAccepted(true)
                .privacyPolicyAccepted(true)
                .cancellationPolicyAccepted(true)
                .build())
            .build();
    }
    
    public static PrimaryGuest createPrimaryGuest() {
        return PrimaryGuest.builder()
            .firstName("张")
            .lastName("三")
            .email("zhangsan@example.com")
            .phone("+86 138 0013 8000")
            .idType("ID_CARD")
            .idNumber("110101199001011234")
            .nationality("CN")
            .build();
    }
    
    public static Room createRoom() {
        return Room.builder()
            .id(1L)
            .roomNumber("2001")
            .roomType(RoomType.DELUXE)
            .basePrice(BigDecimal.valueOf(400))
            .maxOccupancy(3)
            .status(RoomStatus.AVAILABLE)
            .build();
    }
}
```

---

## 11. 测试配置

### 测试配置文件: `application-test.properties`

```properties
# 数据库配置 - 使用内存数据库
spring.datasource.url=jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE
spring.datasource.driver-class-name=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=

# JPA配置
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true

# 日志配置
logging.level.com.hotel.reservation=DEBUG
logging.level.org.springframework.web=DEBUG

# 测试专用配置
app.test.jwt.secret=test-secret-key-for-jwt-token-generation
app.test.jwt.expiration=3600000

# 外部服务Mock配置
app.payment.mock.enabled=true
app.notification.mock.enabled=true
```

---

## 12. 测试执行计划

### 测试执行策略

| 测试阶段 | 测试类型 | 执行频率 | 目标覆盖率 |
|----------|----------|----------|------------|
| 开发阶段 | 单元测试 | 每次提交 | 80% |
| 集成阶段 | 集成测试 | 每日构建 | 70% |
| 测试阶段 | 端到端测试 | 每个迭代 | 90% |
| 发布前 | 性能测试 | 发布前 | - |

### 持续集成配置

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up JDK 11
      uses: actions/setup-java@v2
      with:
        java-version: '11'
        distribution: 'temurin'
    
    - name: Cache Maven packages
      uses: actions/cache@v2
      with:
        path: ~/.m2
        key: ${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}
    
    - name: Run Unit Tests
      run: mvn test -Dtest="**/*Test"
    
    - name: Run Integration Tests
      run: mvn test -Dtest="**/*IT"
    
    - name: Generate Test Report
      run: mvn jacoco:report
    
    - name: Upload Coverage to Codecov
      uses: codecov/codecov-action@v1
```

---

## 13. 测试报告

### 测试用例统计

| 测试模块 | 测试用例数 | 通过率目标 | 覆盖率目标 |
|----------|------------|------------|------------|
| 房间可用性检查 | 15 | 100% | 90% |
| 价格计算 | 12 | 100% | 85% |
| 创建预订 | 20 | 100% | 90% |
| 支付处理 | 18 | 100% | 85% |
| 预订查询 | 10 | 100% | 80% |
| 预订取消 | 15 | 100% | 85% |
| **总计** | **90** | **100%** | **87%** |

### 测试环境要求

- **JDK版本**: 11+
- **Maven版本**: 3.6+
- **数据库**: H2 (内存数据库)
- **外部依赖**: Mock服务

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0 | 2025-07-16 | 初始版本创建 |

---

**测试负责人**: 测试工程师  
**审核人**: 技术负责人  
**最后更新**: 2025年7月16日
