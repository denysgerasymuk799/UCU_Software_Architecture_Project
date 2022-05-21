/* eslint-disable no-undef */
/* eslint-disable no-console */
import React from 'react'

const TableRow = (obj, key) => {
  return (
    <tr>
        <td>
            <span className="bold-date">{ new Date(obj.trans.date * 1000).toISOString().slice(0, 10) }</span>
            {/* <br />
            18:42 */}
        </td>
        <td>
            <i className="fa fa-arrow-alt-circle-up" aria-hidden="true"></i>
            <span className="bold-date">
                {(() => {
                    switch (obj.trans.receiver_card_id) {
                        case 'BALANCE-TOP-UP':   return ` ${obj.trans.card_id}`
                        case localStorage.getItem('card_id'):  return ` ${obj.trans.card_id}`
                        default:                 return ` ${obj.trans.receiver_card_id}`
                    }
                })()}
            </span>
        </td>
        <td>
            <span className="bold-date">
                {(() => {
                    switch (obj.trans.receiver_card_id) {
                        case 'BALANCE-TOP-UP':  return obj.trans.amount;
                        case localStorage.getItem('card_id'):  return obj.trans.amount;
                        default:                 return `-${obj.trans.amount}`;
                    }
                })()}
            </span>.00 
        </td>
        <td className={(() => {
                switch (obj.trans.status) {
                    case 'COMPLETED':   return 'bold-success';
                    default:            return 'bold-error';
                }
            })()}
        >
            <i className="fa fa-circle" aria-hidden="true"></i>
            <span>
                {(() => {
                    switch (obj.trans.status) {
                        case 'COMPLETED':   return ' успішно';
                        case 'NEW':         return ' опрацьовується';
                        default:            return ' помилка';
                    }
                })()}
            </span>
        </td>
    </tr>
  )
}

export default TableRow

