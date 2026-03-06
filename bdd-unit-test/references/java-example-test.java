package com.example.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;
import java.util.List;
import java.util.Collections;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

/**
 * Java/JUnit 5 BDD 單元測試範例
 *
 * 示範：用戶服務的單元測試，使用 Mockito + AssertJ
 * 命名規範：Given條件_When動作_Should預期行為
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("UserService 單元測試")
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private EmailService emailService;

    @InjectMocks
    private UserService userService;

    @Nested
    @DisplayName("findById 方法")
    class FindByIdTests {

        @Test
        @DisplayName("應該在用戶存在時返回用戶")
        void GivenUserExists_WhenFindById_ShouldReturnUser() {
            // Given - 用戶存在於資料庫
            User expectedUser = new User(1L, "john@example.com", "John");
            when(userRepository.findById(1L)).thenReturn(Optional.of(expectedUser));

            // When - 查詢用戶
            Optional<User> result = userService.findById(1L);

            // Then - 應返回該用戶
            assertThat(result)
                .isPresent()
                .hasValueSatisfying(user -> {
                    assertThat(user.getId()).isEqualTo(1L);
                    assertThat(user.getEmail()).isEqualTo("john@example.com");
                });
        }

        @Test
        @DisplayName("應該在用戶不存在時返回空")
        void GivenUserNotExists_WhenFindById_ShouldReturnEmpty() {
            // Given - 用戶不存在
            when(userRepository.findById(999L)).thenReturn(Optional.empty());

            // When - 查詢用戶
            Optional<User> result = userService.findById(999L);

            // Then - 應返回空 Optional
            assertThat(result).isEmpty();
        }
    }

    @Nested
    @DisplayName("createUser 方法")
    class CreateUserTests {

        @Test
        @DisplayName("應該創建用戶並發送歡迎郵件")
        void GivenValidRequest_WhenCreateUser_ShouldCreateAndSendEmail() {
            // Given - 準備新用戶資料
            CreateUserRequest request = new CreateUserRequest("jane@example.com", "Jane");
            User savedUser = new User(2L, "jane@example.com", "Jane");

            when(userRepository.existsByEmail("jane@example.com")).thenReturn(false);
            when(userRepository.save(any(User.class))).thenReturn(savedUser);

            // When - 創建用戶
            User result = userService.createUser(request);

            // Then - 用戶應被創建且發送歡迎郵件
            assertThat(result.getId()).isEqualTo(2L);
            assertThat(result.getEmail()).isEqualTo("jane@example.com");

            // 驗證郵件服務被呼叫
            verify(emailService, times(1)).sendWelcomeEmail("jane@example.com", "Jane");
        }

        @Test
        @DisplayName("應該在 email 已存在時拋出例外")
        void GivenEmailAlreadyExists_WhenCreateUser_ShouldThrowException() {
            // Given - Email 已被使用
            CreateUserRequest request = new CreateUserRequest("existing@example.com", "Test");
            when(userRepository.existsByEmail("existing@example.com")).thenReturn(true);

            // When & Then - 應拋出 DuplicateEmailException
            assertThatThrownBy(() -> userService.createUser(request))
                .isInstanceOf(DuplicateEmailException.class)
                .hasMessage("Email already registered: existing@example.com");

            // 驗證不應嘗試儲存或發送郵件
            verify(userRepository, never()).save(any());
            verify(emailService, never()).sendWelcomeEmail(anyString(), anyString());
        }

        @Test
        @DisplayName("應該在 email 格式無效時拋出驗證例外")
        void GivenInvalidEmailFormat_WhenCreateUser_ShouldThrowValidationException() {
            // Given - 無效的 email 格式
            CreateUserRequest request = new CreateUserRequest("invalid-email", "Test");

            // When & Then - 應拋出 ValidationException
            assertThatThrownBy(() -> userService.createUser(request))
                .isInstanceOf(ValidationException.class)
                .hasMessageContaining("Invalid email format");
        }
    }

    @Nested
    @DisplayName("findAllActive 方法")
    class FindAllActiveTests {

        @Test
        @DisplayName("應該返回所有活躍用戶")
        void GivenActiveUsersExist_WhenFindAllActive_ShouldReturnActiveUsers() {
            // Given - 存在活躍用戶
            List<User> activeUsers = List.of(
                new User(1L, "user1@example.com", "User1"),
                new User(2L, "user2@example.com", "User2")
            );
            when(userRepository.findByActiveTrue()).thenReturn(activeUsers);

            // When - 查詢活躍用戶
            List<User> result = userService.findAllActive();

            // Then - 應返回活躍用戶列表
            assertThat(result)
                .hasSize(2)
                .extracting(User::getEmail)
                .containsExactly("user1@example.com", "user2@example.com");
        }

        @Test
        @DisplayName("應該在沒有活躍用戶時返回空列表")
        void GivenNoActiveUsers_WhenFindAllActive_ShouldReturnEmptyList() {
            // Given - 沒有活躍用戶
            when(userRepository.findByActiveTrue()).thenReturn(Collections.emptyList());

            // When - 查詢活躍用戶
            List<User> result = userService.findAllActive();

            // Then - 應返回空列表（非 null）
            assertThat(result)
                .isNotNull()
                .isEmpty();
        }
    }

    @Nested
    @DisplayName("deactivateUser 方法")
    class DeactivateUserTests {

        @Test
        @DisplayName("應該停用用戶帳號")
        void GivenActiveUser_WhenDeactivate_ShouldSetInactive() {
            // Given - 用戶存在且為活躍狀態
            User activeUser = new User(1L, "user@example.com", "User");
            activeUser.setActive(true);
            when(userRepository.findById(1L)).thenReturn(Optional.of(activeUser));

            // When - 停用用戶
            userService.deactivateUser(1L);

            // Then - 用戶狀態應被更新
            verify(userRepository).save(argThat(user ->
                user.getId().equals(1L) && !user.isActive()
            ));
        }

        @Test
        @DisplayName("應該在用戶不存在時拋出 UserNotFoundException")
        void GivenUserNotExists_WhenDeactivate_ShouldThrowException() {
            // Given - 用戶不存在
            when(userRepository.findById(999L)).thenReturn(Optional.empty());

            // When & Then - 應拋出 UserNotFoundException
            assertThatThrownBy(() -> userService.deactivateUser(999L))
                .isInstanceOf(UserNotFoundException.class)
                .hasMessage("User not found with id: 999");
        }
    }
}
