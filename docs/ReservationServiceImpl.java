// 预订服务核心实现示例代码

/**
 * 预订服务接口
 */
public interface ReservationService {
    ReservationResponse createReservation(ReservationRequest request);
    boolean checkAvailability(Long roomId, LocalDate checkIn, LocalDate checkOut);
    BigDecimal calculatePrice(Long roomId, LocalDate checkIn, LocalDate checkOut);
    boolean cancelReservation(Long reservationId);
    Reservation getReservationById(Long reservationId);
    List<Reservation> getReservationsByUser(Long userId);
}

/**
 * 预订服务实现类
 */
@Service
@Transactional
@Slf4j
public class ReservationServiceImpl implements ReservationService {
    
    private final RoomService roomService;
    private final PaymentService paymentService;
    private final NotificationService notificationService;
    private final ReservationRepository reservationRepository;
    private final ReservationValidator reservationValidator;
    private final PriceCalculator priceCalculator;
    
    public ReservationServiceImpl(
            RoomService roomService,
            PaymentService paymentService,
            NotificationService notificationService,
            ReservationRepository reservationRepository,
            ReservationValidator reservationValidator,
            PriceCalculator priceCalculator) {
        this.roomService = roomService;
        this.paymentService = paymentService;
        this.notificationService = notificationService;
        this.reservationRepository = reservationRepository;
        this.reservationValidator = reservationValidator;
        this.priceCalculator = priceCalculator;
    }
    
    @Override
    @Transactional
    public ReservationResponse createReservation(ReservationRequest request) {
        log.info("开始创建预订, roomId: {}, checkIn: {}, checkOut: {}", 
                request.getRoomId(), request.getCheckInDate(), request.getCheckOutDate());
        
        try {
            // 1. 验证预订请求
            validateReservationRequest(request);
            
            // 2. 检查房间可用性并锁定
            if (!checkAndLockRoom(request.getRoomId(), request.getCheckInDate(), request.getCheckOutDate())) {
                throw new RoomNotAvailableException(request.getRoomId(), 
                    new DateRange(request.getCheckInDate(), request.getCheckOutDate()));
            }
            
            // 3. 计算价格
            BigDecimal totalAmount = calculatePrice(request.getRoomId(), 
                    request.getCheckInDate(), request.getCheckOutDate());
            
            // 4. 创建预订实体
            Reservation reservation = createReservationEntity(request, totalAmount);
            reservation = reservationRepository.save(reservation);
            
            // 5. 处理支付
            PaymentResult paymentResult = processPayment(reservation, request.getPaymentInfo());
            
            if (paymentResult.isSuccess()) {
                // 6. 确认预订
                reservation.setStatus(ReservationStatus.CONFIRMED);
                reservation = reservationRepository.save(reservation);
                
                // 7. 发送确认通知
                notificationService.sendReservationConfirmation(reservation);
                
                log.info("预订创建成功, reservationId: {}", reservation.getReservationId());
                return buildSuccessResponse(reservation, paymentResult);
            } else {
                // 支付失败，取消预订并释放房间
                handlePaymentFailure(reservation);
                return buildPaymentFailureResponse(paymentResult);
            }
            
        } catch (Exception e) {
            log.error("预订创建失败", e);
            // 释放可能已锁定的房间
            unlockRoom(request.getRoomId(), request.getCheckInDate(), request.getCheckOutDate());
            throw e;
        }
    }
    
    @Override
    public boolean checkAvailability(Long roomId, LocalDate checkIn, LocalDate checkOut) {
        return roomService.checkRoomAvailability(roomId, checkIn, checkOut);
    }
    
    @Override
    public BigDecimal calculatePrice(Long roomId, LocalDate checkIn, LocalDate checkOut) {
        return priceCalculator.calculateTotalPrice(roomId, checkIn, checkOut);
    }
    
    @Override
    @Transactional
    public boolean cancelReservation(Long reservationId) {
        log.info("取消预订, reservationId: {}", reservationId);
        
        Reservation reservation = getReservationById(reservationId);
        if (reservation == null) {
            throw new ReservationNotFoundException(reservationId);
        }
        
        if (!reservation.canBeCancelled()) {
            throw new CancellationNotAllowedException(reservationId);
        }
        
        // 更新预订状态
        reservation.setStatus(ReservationStatus.CANCELLED);
        reservation.setCancelledAt(LocalDateTime.now());
        reservationRepository.save(reservation);
        
        // 释放房间锁定
        unlockRoom(reservation.getRoomId(), reservation.getCheckInDate(), reservation.getCheckOutDate());
        
        // 处理退款
        processRefund(reservation);
        
        // 发送取消通知
        notificationService.sendCancellationNotification(reservation);
        
        log.info("预订取消成功, reservationId: {}", reservationId);
        return true;
    }
    
    @Override
    public Reservation getReservationById(Long reservationId) {
        return reservationRepository.findById(reservationId)
                .orElseThrow(() -> new ReservationNotFoundException(reservationId));
    }
    
    @Override
    public List<Reservation> getReservationsByUser(Long userId) {
        return reservationRepository.findByUserIdOrderByCreatedAtDesc(userId);
    }
    
    private void validateReservationRequest(ReservationRequest request) {
        List<ValidationError> errors = reservationValidator.validate(request);
        if (!errors.isEmpty()) {
            throw new InvalidReservationException(errors);
        }
    }
    
    private boolean checkAndLockRoom(Long roomId, LocalDate checkIn, LocalDate checkOut) {
        if (roomService.checkRoomAvailability(roomId, checkIn, checkOut)) {
            roomService.lockRoom(roomId, checkIn, checkOut);
            return true;
        }
        return false;
    }
    
    private Reservation createReservationEntity(ReservationRequest request, BigDecimal totalAmount) {
        return Reservation.builder()
                .userId(request.getUserId())
                .roomId(request.getRoomId())
                .checkInDate(request.getCheckInDate())
                .checkOutDate(request.getCheckOutDate())
                .guestCount(request.getGuestCount())
                .specialRequests(request.getSpecialRequests())
                .totalAmount(totalAmount)
                .status(ReservationStatus.PENDING)
                .createdAt(LocalDateTime.now())
                .build();
    }
    
    private PaymentResult processPayment(Reservation reservation, PaymentInfo paymentInfo) {
        PaymentRequest paymentRequest = PaymentRequest.builder()
                .amount(reservation.getTotalAmount())
                .currency("CNY")
                .paymentMethod(paymentInfo.getPaymentMethod())
                .paymentInfo(paymentInfo)
                .orderId(reservation.getReservationId().toString())
                .build();
        
        return paymentService.processPayment(paymentRequest);
    }
    
    private void handlePaymentFailure(Reservation reservation) {
        reservation.setStatus(ReservationStatus.CANCELLED);
        reservationRepository.save(reservation);
        unlockRoom(reservation.getRoomId(), reservation.getCheckInDate(), reservation.getCheckOutDate());
    }
    
    private void unlockRoom(Long roomId, LocalDate checkIn, LocalDate checkOut) {
        try {
            roomService.unlockRoom(roomId, checkIn, checkOut);
        } catch (Exception e) {
            log.error("释放房间锁定失败, roomId: {}", roomId, e);
        }
    }
    
    private void processRefund(Reservation reservation) {
        // 根据取消政策计算退款金额
        BigDecimal refundAmount = calculateRefundAmount(reservation);
        if (refundAmount.compareTo(BigDecimal.ZERO) > 0) {
            paymentService.processRefund(reservation.getPayments().get(0).getPaymentId(), refundAmount);
        }
    }
    
    private BigDecimal calculateRefundAmount(Reservation reservation) {
        // 简化的退款计算逻辑
        long daysToCheckIn = ChronoUnit.DAYS.between(LocalDate.now(), reservation.getCheckInDate());
        if (daysToCheckIn >= 7) {
            return reservation.getTotalAmount(); // 全额退款
        } else if (daysToCheckIn >= 1) {
            return reservation.getTotalAmount().multiply(new BigDecimal("0.8")); // 80%退款
        } else {
            return BigDecimal.ZERO; // 无退款
        }
    }
    
    private ReservationResponse buildSuccessResponse(Reservation reservation, PaymentResult paymentResult) {
        return ReservationResponse.builder()
                .reservationId(reservation.getReservationId())
                .status("CONFIRMED")
                .message("预订创建成功")
                .totalAmount(reservation.getTotalAmount())
                .paymentStatus(paymentResult.getStatus().name())
                .confirmationNumber(generateConfirmationNumber(reservation))
                .build();
    }
    
    private ReservationResponse buildPaymentFailureResponse(PaymentResult paymentResult) {
        return ReservationResponse.builder()
                .status("PAYMENT_FAILED")
                .message("支付失败: " + paymentResult.getMessage())
                .paymentStatus(paymentResult.getStatus().name())
                .build();
    }
    
    private String generateConfirmationNumber(Reservation reservation) {
        return "HTL" + LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"))
                + String.format("%03d", reservation.getReservationId() % 1000);
    }
}

/**
 * 预订实体类
 */
@Entity
@Table(name = "reservations")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Reservation {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long reservationId;
    
    @Column(nullable = false)
    private Long userId;
    
    @Column(nullable = false)
    private Long roomId;
    
    @Column(nullable = false)
    private LocalDate checkInDate;
    
    @Column(nullable = false)
    private LocalDate checkOutDate;
    
    private Integer guestCount;
    
    private String specialRequests;
    
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal totalAmount;
    
    @Enumerated(EnumType.STRING)
    private ReservationStatus status;
    
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private LocalDateTime cancelledAt;
    
    @OneToMany(mappedBy = "reservation", cascade = CascadeType.ALL)
    private List<Payment> payments = new ArrayList<>();
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "room_id", insertable = false, updatable = false)
    private Room room;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", insertable = false, updatable = false)
    private User user;
    
    /**
     * 计算住宿天数
     */
    public Integer calculateNights() {
        return (int) ChronoUnit.DAYS.between(checkInDate, checkOutDate);
    }
    
    /**
     * 验证日期有效性
     */
    public boolean isValidDates() {
        return checkInDate != null && checkOutDate != null 
                && checkInDate.isBefore(checkOutDate)
                && !checkInDate.isBefore(LocalDate.now());
    }
    
    /**
     * 检查是否可以取消
     */
    public boolean canBeCancelled() {
        return status == ReservationStatus.CONFIRMED 
                && checkInDate.isAfter(LocalDate.now());
    }
    
    /**
     * 获取住宿时长
     */
    public Period getStayDuration() {
        return Period.between(checkInDate, checkOutDate);
    }
    
    @PreUpdate
    public void preUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}

/**
 * 预订请求DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReservationRequest {
    
    @NotNull(message = "房间ID不能为空")
    private Long roomId;
    
    @NotNull(message = "用户ID不能为空")
    private Long userId;
    
    @NotNull(message = "入住日期不能为空")
    @Future(message = "入住日期必须是未来日期")
    private LocalDate checkInDate;
    
    @NotNull(message = "退房日期不能为空")
    @Future(message = "退房日期必须是未来日期")
    private LocalDate checkOutDate;
    
    @Min(value = 1, message = "客人数量至少为1")
    @Max(value = 10, message = "客人数量不能超过10")
    private Integer guestCount = 1;
    
    @Size(max = 500, message = "特殊要求不能超过500字符")
    private String specialRequests;
    
    @NotNull(message = "支付信息不能为空")
    @Valid
    private PaymentInfo paymentInfo;
    
    /**
     * 验证请求参数
     */
    public List<ValidationError> validate() {
        List<ValidationError> errors = new ArrayList<>();
        
        if (checkInDate != null && checkOutDate != null) {
            if (!checkInDate.isBefore(checkOutDate)) {
                errors.add(new ValidationError("checkOutDate", "退房日期必须晚于入住日期"));
            }
            
            if (ChronoUnit.DAYS.between(checkInDate, checkOutDate) > 30) {
                errors.add(new ValidationError("dateRange", "住宿天数不能超过30天"));
            }
        }
        
        return errors;
    }
}

/**
 * 预订响应DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReservationResponse {
    private Long reservationId;
    private String status;
    private String message;
    private BigDecimal totalAmount;
    private String paymentStatus;
    private String confirmationNumber;
}

/**
 * 预订状态枚举
 */
public enum ReservationStatus {
    PENDING("待处理"),
    CONFIRMED("已确认"),
    CANCELLED("已取消"),
    COMPLETED("已完成"),
    EXPIRED("已过期");
    
    private final String description;
    
    ReservationStatus(String description) {
        this.description = description;
    }
    
    public String getDescription() {
        return description;
    }
}

/**
 * 预订仓储接口
 */
@Repository
public interface ReservationRepository extends JpaRepository<Reservation, Long> {
    
    List<Reservation> findByUserIdOrderByCreatedAtDesc(Long userId);
    
    List<Reservation> findByRoomIdAndStatusIn(Long roomId, List<ReservationStatus> statuses);
    
    @Query("SELECT r FROM Reservation r WHERE r.roomId = :roomId " +
           "AND r.status IN ('CONFIRMED', 'PENDING') " +
           "AND ((r.checkInDate <= :checkOut AND r.checkOutDate > :checkIn))")
    List<Reservation> findOverlappingReservations(@Param("roomId") Long roomId,
                                                  @Param("checkIn") LocalDate checkIn,
                                                  @Param("checkOut") LocalDate checkOut);
    
    @Modifying
    @Query("UPDATE Reservation r SET r.status = :status WHERE r.reservationId = :reservationId")
    void updateStatus(@Param("reservationId") Long reservationId, 
                     @Param("status") ReservationStatus status);
    
    List<Reservation> findByStatusAndCheckInDateBefore(ReservationStatus status, LocalDate date);
    
    @Query("SELECT COUNT(r) FROM Reservation r WHERE r.roomId = :roomId " +
           "AND r.checkInDate >= :startDate AND r.checkInDate < :endDate " +
           "AND r.status = 'CONFIRMED'")
    long countConfirmedReservations(@Param("roomId") Long roomId,
                                   @Param("startDate") LocalDate startDate,
                                   @Param("endDate") LocalDate endDate);
}

/**
 * 预订验证器
 */
@Component
public class ReservationValidator {
    
    private final RoomService roomService;
    
    public ReservationValidator(RoomService roomService) {
        this.roomService = roomService;
    }
    
    public List<ValidationError> validate(ReservationRequest request) {
        List<ValidationError> errors = new ArrayList<>();
        
        // 基本参数验证
        errors.addAll(validateBasicParameters(request));
        
        // 业务规则验证
        errors.addAll(validateBusinessRules(request));
        
        return errors;
    }
    
    private List<ValidationError> validateBasicParameters(ReservationRequest request) {
        List<ValidationError> errors = new ArrayList<>();
        
        if (request.getRoomId() == null) {
            errors.add(new ValidationError("roomId", "房间ID不能为空"));
        }
        
        if (request.getCheckInDate() == null) {
            errors.add(new ValidationError("checkInDate", "入住日期不能为空"));
        }
        
        if (request.getCheckOutDate() == null) {
            errors.add(new ValidationError("checkOutDate", "退房日期不能为空"));
        }
        
        return errors;
    }
    
    private List<ValidationError> validateBusinessRules(ReservationRequest request) {
        List<ValidationError> errors = new ArrayList<>();
        
        // 验证房间是否存在
        if (request.getRoomId() != null) {
            Room room = roomService.getRoomById(request.getRoomId());
            if (room == null) {
                errors.add(new ValidationError("roomId", "指定的房间不存在"));
            } else {
                // 验证客人数量是否超过房间容量
                if (request.getGuestCount() != null && request.getGuestCount() > room.getMaxOccupancy()) {
                    errors.add(new ValidationError("guestCount", 
                            "客人数量不能超过房间最大容量: " + room.getMaxOccupancy()));
                }
            }
        }
        
        // 验证日期范围
        if (request.getCheckInDate() != null && request.getCheckOutDate() != null) {
            if (!request.getCheckInDate().isBefore(request.getCheckOutDate())) {
                errors.add(new ValidationError("dateRange", "退房日期必须晚于入住日期"));
            }
            
            if (request.getCheckInDate().isBefore(LocalDate.now())) {
                errors.add(new ValidationError("checkInDate", "入住日期不能早于今天"));
            }
            
            long nights = ChronoUnit.DAYS.between(request.getCheckInDate(), request.getCheckOutDate());
            if (nights > 30) {
                errors.add(new ValidationError("dateRange", "住宿天数不能超过30天"));
            }
        }
        
        return errors;
    }
}

/**
 * 价格计算器
 */
@Component
public class PriceCalculator {
    
    private final RoomService roomService;
    
    public PriceCalculator(RoomService roomService) {
        this.roomService = roomService;
    }
    
    public BigDecimal calculateTotalPrice(Long roomId, LocalDate checkIn, LocalDate checkOut) {
        Room room = roomService.getRoomById(roomId);
        if (room == null) {
            throw new IllegalArgumentException("房间不存在: " + roomId);
        }
        
        long nights = ChronoUnit.DAYS.between(checkIn, checkOut);
        BigDecimal basePrice = room.getBasePrice().multiply(BigDecimal.valueOf(nights));
        
        // 应用季节性定价
        BigDecimal seasonalPrice = applySeasonalPricing(basePrice, checkIn, checkOut);
        
        // 应用周末定价
        BigDecimal weekendPrice = applyWeekendPricing(seasonalPrice, checkIn, checkOut);
        
        // 计算税费
        BigDecimal taxes = calculateTaxes(weekendPrice);
        
        return weekendPrice.add(taxes);
    }
    
    private BigDecimal applySeasonalPricing(BigDecimal basePrice, LocalDate checkIn, LocalDate checkOut) {
        // 简化的季节性定价逻辑
        Month checkInMonth = checkIn.getMonth();
        
        if (checkInMonth == Month.JULY || checkInMonth == Month.AUGUST) {
            // 夏季旺季，价格上涨20%
            return basePrice.multiply(new BigDecimal("1.2"));
        } else if (checkInMonth == Month.DECEMBER || checkInMonth == Month.JANUARY) {
            // 冬季旺季，价格上涨15%
            return basePrice.multiply(new BigDecimal("1.15"));
        }
        
        return basePrice;
    }
    
    private BigDecimal applyWeekendPricing(BigDecimal price, LocalDate checkIn, LocalDate checkOut) {
        // 计算周末天数
        long weekendNights = 0;
        LocalDate current = checkIn;
        
        while (current.isBefore(checkOut)) {
            DayOfWeek dayOfWeek = current.getDayOfWeek();
            if (dayOfWeek == DayOfWeek.FRIDAY || dayOfWeek == DayOfWeek.SATURDAY) {
                weekendNights++;
            }
            current = current.plusDays(1);
        }
        
        if (weekendNights > 0) {
            // 周末价格上涨10%
            BigDecimal weekendSurcharge = price.multiply(new BigDecimal("0.1"))
                    .multiply(BigDecimal.valueOf(weekendNights))
                    .divide(BigDecimal.valueOf(ChronoUnit.DAYS.between(checkIn, checkOut)), 2, RoundingMode.HALF_UP);
            return price.add(weekendSurcharge);
        }
        
        return price;
    }
    
    private BigDecimal calculateTaxes(BigDecimal subtotal) {
        // 6%的城市税
        return subtotal.multiply(new BigDecimal("0.06"));
    }
}

/**
 * 自定义异常类
 */
public class HotelReservationException extends RuntimeException {
    private final String errorCode;
    private final LocalDateTime timestamp;
    
    public HotelReservationException(String errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
        this.timestamp = LocalDateTime.now();
    }
    
    public String getErrorCode() {
        return errorCode;
    }
    
    public LocalDateTime getTimestamp() {
        return timestamp;
    }
}

public class RoomNotAvailableException extends HotelReservationException {
    private final Long roomId;
    private final DateRange requestedDates;
    
    public RoomNotAvailableException(Long roomId, DateRange requestedDates) {
        super("ROOM_NOT_AVAILABLE", 
              String.format("房间 %d 在 %s 至 %s 期间不可用", roomId, 
                           requestedDates.getStartDate(), requestedDates.getEndDate()));
        this.roomId = roomId;
        this.requestedDates = requestedDates;
    }
    
    public Long getRoomId() {
        return roomId;
    }
    
    public DateRange getRequestedDates() {
        return requestedDates;
    }
}

public class InvalidReservationException extends HotelReservationException {
    private final List<ValidationError> validationErrors;
    
    public InvalidReservationException(List<ValidationError> validationErrors) {
        super("VALIDATION_ERROR", "预订请求验证失败");
        this.validationErrors = validationErrors;
    }
    
    public List<ValidationError> getValidationErrors() {
        return validationErrors;
    }
}

/**
 * 验证错误类
 */
@Data
@AllArgsConstructor
public class ValidationError {
    private String field;
    private String message;
}

/**
 * 日期范围类
 */
@Data
@AllArgsConstructor
public class DateRange {
    private LocalDate startDate;
    private LocalDate endDate;
}
