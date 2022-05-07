/* eslint-disable jsx-a11y/media-has-caption */
import React from 'react'
import NavDropdown from '../../modules/NavDropdown'
import SettingsModal from '../../modules/SettingsModal'
import PaymentModal from '../../modules/PaymentModal'
import AddMoneyModal from '../../modules/AddMoneyModal'

const ProfileView = () => (
  <div>
    <header>
      <h1 class="main-logo">
        <a href="index.html">
          unobank
          <span class="gray">| Ukrainian Catholic University</span>
        </a>
      </h1>
      <button data-bs-toggle="dropdown">
        +38 (096) 537 82 16
        <i class="fa fa-angle-down" aria-hidden="true"></i>
      </button>
      <NavDropdown />
    </header>

    <SettingsModal />
    <PaymentModal />
    <AddMoneyModal />

    <section id="sidebar">
      <div class="item-wrapper pb-16">
        <div class="img-wrapper">
          <img src="img/ava.jpeg" alt="" />
        </div>
        <h1>Лопушанський Дмитро Андрійович</h1>
        <p class="mini-title">Рахунок</p>
        <div class="button-like">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"> <path fill-rule="evenodd" clip-rule="evenodd" d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22ZM12.761 10.433L8.46238 9.33694L8.19524 10.3599L11.4495 11.1881C11.2768 11.2693 11.0987 11.3532 10.9152 11.4398C10.7317 11.521 10.5483 11.6076 10.3648 11.6996L8.02524 11.1069L7.75 12.1218L9.13429 12.4709C8.81587 12.7361 8.55683 13.0474 8.35714 13.4046C8.16286 13.7618 8.06571 14.1949 8.06571 14.7037C8.06571 15.2016 8.15476 15.6536 8.33286 16.0595C8.51635 16.4655 8.78079 16.8119 9.12619 17.0988C9.47698 17.3857 9.90333 17.6076 10.4052 17.7645C10.9071 17.9215 11.4819 18 12.1295 18C12.5019 18 12.8689 17.9621 13.2305 17.8863C13.5921 17.816 13.9375 17.7131 14.2667 17.5778C14.6013 17.4425 14.9143 17.2801 15.2057 17.0907C15.4971 16.9012 15.7562 16.6901 15.9829 16.4574L15.3433 15.41C15.2894 15.3342 15.2192 15.272 15.1329 15.2233C15.0465 15.1691 14.9548 15.1421 14.8576 15.1421C14.7173 15.1421 14.5689 15.1989 14.4124 15.3126C14.2613 15.4208 14.0778 15.5426 13.8619 15.6779C13.646 15.8133 13.3924 15.9378 13.101 16.0514C12.8149 16.1597 12.4695 16.2138 12.0648 16.2138C11.5035 16.2138 11.0583 16.1137 10.729 15.9134C10.4052 15.7131 10.2433 15.3884 10.2433 14.9391C10.2433 14.7118 10.2757 14.5061 10.3405 14.3221C10.4106 14.138 10.5051 13.9729 10.6238 13.8268C10.7479 13.6806 10.891 13.548 11.0529 13.429C11.2202 13.3099 11.401 13.1989 11.5952 13.0961L15.5376 14.0866L15.8048 13.0636L13.109 12.3897C13.2817 12.3085 13.4517 12.2273 13.619 12.1461C13.7917 12.0595 13.9563 11.9648 14.1129 11.862L15.9748 12.3248L16.25 11.3099L15.06 11.0095C15.2435 10.7713 15.3865 10.498 15.489 10.1894C15.597 9.88092 15.651 9.52368 15.651 9.11773C15.651 8.70636 15.5646 8.31123 15.3919 7.93234C15.2246 7.55345 14.979 7.22327 14.6552 6.94181C14.3314 6.65494 13.9321 6.4276 13.4571 6.25981C12.9822 6.0866 12.4371 6 11.8219 6C11.1311 6 10.4943 6.10825 9.91143 6.32476C9.32857 6.54127 8.83206 6.84438 8.4219 7.2341L8.95619 8.26522C9.02095 8.37889 9.09111 8.46279 9.16667 8.51691C9.24222 8.56563 9.33397 8.58999 9.44191 8.58999C9.54984 8.58999 9.67127 8.54939 9.80619 8.4682C9.94111 8.3816 10.1003 8.28687 10.2838 8.18403C10.4673 8.08119 10.6805 7.98917 10.9233 7.90798C11.1716 7.82138 11.463 7.77808 11.7976 7.77808C12.0783 7.77808 12.3238 7.81326 12.5343 7.88363C12.7448 7.94858 12.9202 8.0406 13.0605 8.15967C13.2008 8.27334 13.306 8.40866 13.3762 8.56563C13.4517 8.7226 13.4895 8.89039 13.4895 9.06901C13.4895 9.3613 13.4248 9.6184 13.2952 9.84032C13.1657 10.0622 12.9876 10.2598 12.761 10.433Z" fill="currentColor"></path> </svg>
          <span>Гривня</span>
        </div>
      </div>
    </section>

    <section id="main-page">
      <div class="item-wrapper">
        <div class="balance-header">
          <span class="main-balance">100</span>
          <span class="coins">.00 ₴</span>
          <div class="buttons">
            <button class="bank-btn black" data-toggle="modal" data-target="#paymentModal">
              <i class="fa fa-plus" aria-hidden="true"></i>
              <span>Створити платіж</span>
            </button>
            <button class="bank-btn" data-toggle="modal" data-target="#addMoneyModal">
              <i class="fa fa-coins" aria-hidden="true"></i>
              <span>Поповнити рахунок</span>
            </button>
          </div>
        </div>
        <div class="transactions">
          <div class="table-responsive">
                <table class="table custom-table">
                  <thead>
                      <tr>
                          <th scope="col">Дата</th>
                          <th scope="col">Контрагент і призначення</th>
                          <th scope="col">Сума (₴)</th>
                          <th scope="col">Статус</th>
                      </tr>
                  </thead>
                  <tbody>
                    <tr>
                        <td>
                          <span class="bold-date">12.03.22</span>
                          <br />
                  18:42
                </td>
                        <td>
                          <i class="fa fa-arrow-alt-circle-up" aria-hidden="true"></i>
                          <span class="bold-date">
                            Лопушанський Дмитро
                          </span>
                          <br />
                  Переказ мiж власними рахунками для поповнення картки
                        </td>
                        <td>
                          <span class="bold-date">-543</span>.00
                        </td>
                        <td class="bold-success">
                          <i class="fa fa-circle" aria-hidden="true"></i>
                          <span>
                            сплачено
                          </span>
                        </td>
                    </tr>
                    <tr>
                        <td>
                          <span class="bold-date">09.03.22</span>
                          <br />
                  19:34
                </td>
                        <td>
                          <i class="fa fa-arrow-alt-circle-up" aria-hidden="true"></i>
                          <span class="bold-date">
                            ГУК Львiв/Львівська тг/18050400
                          </span>
                          <br />
                  *;101;3744406937;18050400; Оплата ЄП за 4 квартал
                        </td>
                        <td>
                          <span class="bold-date">-10 852</span>.16
                        </td>
                        <td class="bold-success">
                          <i class="fa fa-circle" aria-hidden="true"></i>
                          <span>
                            сплачено
                          </span>
                        </td>
                    </tr>
                    <tr>
                        <td>
                          <span class="bold-date">12.03.22</span>
                          <br />
                  18:42
                </td>
                        <td>
                          <i class="fa fa-arrow-alt-circle-up" aria-hidden="true"></i>
                          <span class="bold-date">
                            Лопушанський Дмитро
                          </span>
                          <br />
                  Переказ мiж власними рахунками для поповнення картки
                        </td>
                        <td>
                          <span class="bold-date">-543</span>.00
                        </td>
                        <td class="bold-success">
                          <i class="fa fa-circle" aria-hidden="true"></i>
                          <span>
                            сплачено
                          </span>
                        </td>
                    </tr>
                    <tr>
                        <td>
                          <span class="bold-date">12.03.22</span>
                          <br />
                  18:42
                </td>
                        <td>
                          <i class="fa fa-arrow-alt-circle-down success-arrow" aria-hidden="true"></i>
                          <span class="bold-date">
                            ТОВ "ЕПАМ СИСТЕМЗ"
                          </span>
                          <br />
                  Оплата (Л) за комп'ютерне програмування, зг. дог.№2
                        </td>
                        <td class="bold-success">
                          <span class="bold-date">29 253</span>.90
                        </td>
                        <td class="bold-success">
                          <i class="fa fa-circle" aria-hidden="true"></i>
                          <span>
                            отримано
                          </span>
                        </td>
                    </tr>
                    <tr>
                        <td>
                          <span class="bold-date">09.12.21</span>
                          <br />
                  13:12
                </td>
                        <td>
                          <i class="fa fa-arrow-alt-circle-up" aria-hidden="true"></i>
                          <span class="bold-date">
                            ГУДПС у Львівській області/71040000
                          </span>
                          <br />
                  *;204;3744406937;71040000, ЄСВ для ФОП,
                        </td>
                        <td>
                          <span class="bold-date">-4 070</span>.45
                        </td>
                        <td class="bold-success">
                          <i class="fa fa-circle" aria-hidden="true"></i>
                          <span>
                            сплачено
                          </span>
                        </td>
                    </tr>
                    <tr>
                        <td>
                          <span class="bold-date">12.03.22</span>
                          <br />
                  18:42
                </td>
                        <td>
                          <i class="fa fa-arrow-alt-circle-up" aria-hidden="true"></i>
                          <span class="bold-date">
                            Лопушанський Дмитро
                          </span>
                          <br />
                  Переказ мiж власними рахунками для поповнення картки
                        </td>
                        <td>
                          <span class="bold-date">-543</span>.00
                        </td>
                        <td class="bold-success">
                          <i class="fa fa-circle" aria-hidden="true"></i>
                          <span>
                            сплачено
                          </span>
                        </td>
                    </tr>
                    <tr>
                        <td>
                          <span class="bold-date">09.03.22</span>
                          <br />
                  19:34
                </td>
                        <td>
                          <i class="fa fa-arrow-alt-circle-up" aria-hidden="true"></i>
                          <span class="bold-date">
                            ГУК Львiв/Львівська тг/18050400
                          </span>
                          <br />
                  *;101;3744406937;18050400; Оплата ЄП за 4 квартал
                        </td>
                        <td>
                          <span class="bold-date">-10 852</span>.16
                        </td>
                        <td class="bold-success">
                          <i class="fa fa-circle" aria-hidden="true"></i>
                          <span>
                            сплачено
                          </span>
                        </td>
                    </tr>
                    <tr>
                        <td>
                          <span class="bold-date">12.03.22</span>
                          <br />
                  18:42
                </td>
                        <td>
                          <i class="fa fa-arrow-alt-circle-up" aria-hidden="true"></i>
                          <span class="bold-date">
                            Лопушанський Дмитро
                          </span>
                          <br />
                  Переказ мiж власними рахунками для поповнення картки
                        </td>
                        <td>
                          <span class="bold-date">-543</span>.00
                        </td>
                        <td class="bold-success">
                          <i class="fa fa-circle" aria-hidden="true"></i>
                          <span>
                            сплачено
                          </span>
                        </td>
                    </tr>
                    <tr>
                        <td>
                          <span class="bold-date">12.03.22</span>
                          <br />
                  18:42
                </td>
                        <td>
                          <i class="fa fa-arrow-alt-circle-down success-arrow" aria-hidden="true"></i>
                          <span class="bold-date">
                            ТОВ "ЕПАМ СИСТЕМЗ"
                          </span>
                          <br />
                  Оплата (Л) за комп'ютерне програмування, зг. дог.№2
                        </td>
                        <td class="bold-success">
                          <span class="bold-date">29 253</span>.90
                        </td>
                        <td class="bold-success">
                          <i class="fa fa-circle" aria-hidden="true"></i>
                          <span>
                            отримано
                          </span>
                        </td>
                    </tr>
                    <tr>
                        <td>
                          <span class="bold-date">09.12.21</span>
                          <br />
                  13:12
                </td>
                        <td>
                          <i class="fa fa-arrow-alt-circle-up" aria-hidden="true"></i>
                          <span class="bold-date">
                            ГУДПС у Львівській області/71040000
                          </span>
                          <br />
                  *;204;3744406937;71040000, ЄСВ для ФОП,
                        </td>
                        <td>
                          <span class="bold-date">-4 070</span>.45
                        </td>
                        <td class="bold-success">
                          <i class="fa fa-circle" aria-hidden="true"></i>
                          <span>
                            сплачено
                          </span>
                        </td>
                    </tr>
                  </tbody>
                </table>
            </div>
            <button class="bank-btn margin-20">
            <span>Завантажити ще</span>
          </button>
        </div>
      </div>
    </section>
  </div>
)

export default ProfileView