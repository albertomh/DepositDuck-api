/**
 * (c) 2024 Alberto Morón Hernández
 */

// `/welcome/` - onboarding flow
function onboardingState(tenancyEndDate) {
    return {
        name: '',
        depositAmount: null,
        tenancyStartDate: '',
        tenancyEndDate: tenancyEndDate || '',
        errors: {
            nameIsInvalid: false,
            depositAmountTooSmall: false,
            datesInWrongOrder: false,
            tenancyIsTooShort: false,
        },
        hasErrors() { Object.values(this.errors).some((value) => value === true); },
        daysBetweenDates(date1, date2) {
            const diffInMs = date2 - date1;
            const msInDay = 1000 * 60 * 60 * 24;
            const diffInDays = Math.floor(diffInMs / msInDay);
            return diffInDays;
        },
        validateDepositAmount() {
            this.errors.depositAmountTooSmall = this.depositAmount < 10;
        },
        validateTenancyDates() {
            if (!this.tenancyStartDate) {
                return;
            }

            const gap = this.daysBetweenDates(
                new Date(this.tenancyStartDate),
                new Date(this.tenancyEndDate)
            );
            this.errors.datesInWrongOrder = gap < 0;
            this.errors.tenancyIsTooShort = (0 < gap < 30);
        },
        validateForm() {
            this.validateTenancyDates();
            this.validateDepositAmount();
        }
    }
}
